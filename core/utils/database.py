from datetime import datetime, timedelta

from typing import Union, List

from sqlalchemy import create_engine, Column, BigInteger, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

from config import Config


class DataBase:
    '''
    Класс для работы с базой данных
    '''
    __instance = None
    conf = Config()
    engine = create_engine(conf.get_db_connection(), echo=False, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    Session = sessionmaker(autoflush=False, bind=engine)
    Base = declarative_base()


    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(DataBase, cls).__new__(cls)
        return cls.__instance


    class Users(Base):
        __tablename__ = "users"

        user_id = Column(BigInteger(), primary_key=True)
        referer = Column(BigInteger())
        payed_up_to = Column(DateTime())


    class Pays(Base):
        __tablename__ = "pays"

        pay_id = Column(BigInteger(), primary_key=True)
        pay_from_user_id = Column(BigInteger())
        pay_message_id = Column(BigInteger())


    Base.metadata.create_all(engine, checkfirst=True)  # создание таблиц


    def add_pay(self, pay_from_user_id: int, pay_message_id: int) -> None:
        '''Добавляет запись об отправленном скрине'''

        with self.Session() as session:
            pay = self.Pays(
                pay_id=self.get_max_pay_id() + 1,
                pay_from_user_id=pay_from_user_id,
                pay_message_id=pay_message_id,
            )
            session.add(pay)
            session.commit()


    def get_max_pay_id(self):
        with self.Session() as session:
            result = session.query(func.max(self.Pays.pay_id)).scalar()
            if result is None:
                return 0
            return result


    def get_pay_by_msg_id(self, msg_id: int) -> Union[Pays, None]:
        '''Возвращает запись об отправке скрина'''

        with self.Session() as session:
            return session.query(self.Pays).filter(self.Pays.pay_message_id == int(msg_id)).first()


    def get_all_users(self) -> List[Union[Users, None]]:
        '''Возвращает список всех пользователей'''

        with self.Session() as session:
            return session.query(self.Users).all()


    def get_all_referals(self, referer: int) -> List[Union[Users, None]]:
        '''Возвращает список всех рефералов'''

        with self.Session() as session:
            return session.query(self.Users).filter(
                self.Users.referer == referer
            ).all()


    def add_user(self, user_id: int, referer: Union[int, None], payed_up_to: datetime) -> None:
        '''Добавляет пользователя в бд'''

        with self.Session() as session:
            user = self.Users(
                user_id=user_id,
                referer=referer,
                payed_up_to=payed_up_to
            )
            session.add(user)
            session.commit()


    def edit_user_payed_up(self, user_id: int, payed_up: datetime) -> None:
        '''Изменяет время подписки пользователя'''

        with self.Session() as session:
            session.query(self.Users).filter(
                self.Users.user_id == int(user_id)
            ).update({
                self.Users.payed_up_to: payed_up
            })
            session.commit()


    def get_user(self, user_id: int) -> Union[Users, None]:
        '''Возвращает пользователя из бд'''

        with self.Session() as session:
            return session.query(self.Users).filter(
                self.Users.user_id == int(user_id)
            ).first()


    def add_subscribe(self, user_id: int, sub: timedelta) -> None:
        '''Добавляет пользователю срок подписки, если была. Дает, если не было'''

        now = datetime.now()
        user = self.get_user(user_id)

        if user is None:
            self.add_user(user_id, None, now + sub)
            return

        if user.payed_up_to > now:
            self.edit_user_payed_up(user_id, user.payed_up_to + sub)
        else:
            self.edit_user_payed_up(user_id, now + sub)


    def edit_user_referer(self, user_id: int, referer: int) -> None:
        '''изменяет реферера пользователя'''

        with self.Session() as session:
            session.query(self.Users).filter(
                self.Users.user_id == user_id
            ).update({
                self.Users.referer: referer
            })
            session.commit()
