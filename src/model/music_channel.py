from __future__ import annotations

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session

from src.db import Base, engine
from src.tools import logger


class MusicChannel(Base):
    __tablename__ = "music_channel"
    guild_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)

    def __repr__(self):
        return f"table: {self.__tablename__}, guild_id: {self.guild_id}, channel_id: {self.channel_id}"

    @staticmethod
    def add(music_channel: MusicChannel):
        logger.info(f"{MusicChannel.__tablename__}: {music_channel} DB에 추가")
        session: Session
        with Session(engine) as session:
            session.add(music_channel)
            session.commit()

    @staticmethod
    def delete(guild_id: int):
        logger.info(f"{MusicChannel.__tablename__}: {guild_id} 길드 DB에서 삭제")
        session: Session
        with Session(engine) as session:
            music_channel = session.get(MusicChannel, guild_id)
            session.delete(music_channel)
            session.commit()

    @staticmethod
    def update(guild_id: int, channel_id: int):
        logger.info(
            f"{MusicChannel.__tablename__}: {guild_id} 길드 음악 채널을 {channel_id}로 변경"
        )
        session: Session
        with Session(engine) as session:
            music_channel = MusicChannel.get(guild_id)
            music_channel.channel_id = channel_id
            session.commit()

    @staticmethod
    def get(guild_id: int):
        session: Session
        with Session(engine) as session:
            return (
                session.query(MusicChannel)
                .filter(MusicChannel.guild_id == guild_id)
                .first()
            )

    @staticmethod
    def get_all():
        session: Session
        with Session(engine) as session:
            return session.query(MusicChannel).all()


MusicChannel.__table__.create(bind=engine, checkfirst=True)
