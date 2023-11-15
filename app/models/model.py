from typing import List

from models import Base
from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

likes_table = Table(
    "likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column(
        "tweet_id",
        ForeignKey("tweets.tweet_id"),
        primary_key=True,
        index=True,
    ),
)

followers = Table(
    "followers",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("followed_id", ForeignKey("users.id"), primary_key=True, index=True),
)


class User(Base):
    """Model User."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True,
    )
    api_key: Mapped[str] = mapped_column(String(length=50), unique=True)
    name: Mapped[str] = mapped_column(String(length=50))
    likes: Mapped[List["Tweet"]] = relationship(
        secondary=likes_table,
        back_populates="likes",
        lazy="select",
        cascade="all, delete",
    )
    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="user",
        lazy="select",
        cascade="all, delete",
    )
    followed: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.follower_id,
        secondaryjoin=id == followers.c.followed_id,
        back_populates="follower",
        lazy="select",
    )
    follower: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers,
        primaryjoin=id == followers.c.followed_id,
        secondaryjoin=id == followers.c.follower_id,
        back_populates="followed",
        lazy="select",
    )


class Tweet(Base):
    """Model tweet."""

    __tablename__ = "tweets"
    tweet_id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True,
    )
    tweet_data: Mapped[str] = mapped_column(String(length=10000))
    tweet_media_ids: Mapped[List[int]] = mapped_column(
        ARRAY(String(200)),
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[List["User"]] = relationship(
        User,
        back_populates="tweets",
        lazy="joined",
    )
    likes: Mapped[List["User"]] = relationship(
        User,
        secondary=likes_table,
        back_populates="likes",
        lazy="joined",
    )
    time_created = Column(DateTime(timezone=True), server_default=func.now())


class Image(Base):
    """Model images."""

    __tablename__ = "images"
    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(length=200))
