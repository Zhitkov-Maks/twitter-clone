from typing import List

from sqlalchemy import String, ForeignKey, Table, Column, ARRAY, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

likes_table = Table(
    "likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("tweet_id", ForeignKey("tweets.tweet_id"), primary_key=True, index=True),
)

followers = Table(
    "followers",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("followed_id", ForeignKey("users.id"), primary_key=True, index=True),
)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    api_key: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    likes: Mapped[List["Tweet"]] = relationship(secondary=likes_table, back_populates="likes", lazy="joined")
    tweets: Mapped[List["Tweet"]] = relationship("Tweet", back_populates="user", lazy="joined",
                                                 cascade="all, delete-orphan")
    followed: Mapped[List["User"]] = relationship(
        'User',
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        back_populates="follower",
        lazy="select"
    )
    follower: Mapped[List["User"]] = relationship(
        'User',
        secondary=followers,
        primaryjoin=id == followers.c.followed_id,
        secondaryjoin=id == followers.c.follower_id,
        back_populates="followed",
        lazy="select"
    )


class Tweet(Base):
    __tablename__ = 'tweets'
    tweet_id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    tweet_data: Mapped[str] = mapped_column(String(10_000))
    tweet_media_ids: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[List[User]] = relationship(User, back_populates="tweets", lazy="joined")
    likes: Mapped[List[User]] = relationship(User, secondary=likes_table, back_populates="likes", lazy="joined")
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return f"{self.user_id} {self.likes}"


class Image(Base):
    __tablename__ = 'images'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(200))
