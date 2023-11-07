"""create tables

Revision ID: 239a9894de14
Revises: 
Create Date: 2023-11-05 23:10:00.994831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "239a9894de14"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_images_id"), "images", ["id"], unique=False)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("api_key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_key"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table(
        "followers",
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.Column("followed_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["followed_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["follower_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("follower_id", "followed_id"),
    )
    op.create_index(
        op.f("ix_followers_followed_id"), "followers", ["followed_id"], unique=False
    )
    op.create_index(
        op.f("ix_followers_follower_id"), "followers", ["follower_id"], unique=False
    )
    op.create_table(
        "tweets",
        sa.Column("tweet_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tweet_data", sa.String(length=10000), nullable=False),
        sa.Column("tweet_media_ids", sa.ARRAY(sa.String(length=200)), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "time_created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("tweet_id"),
    )
    op.create_index(op.f("ix_tweets_tweet_id"), "tweets", ["tweet_id"], unique=False)
    op.create_index(op.f("ix_tweets_user_id"), "tweets", ["user_id"], unique=False)
    op.create_table(
        "likes",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tweet_id"],
            ["tweets.tweet_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "tweet_id"),
    )
    op.create_index(op.f("ix_likes_tweet_id"), "likes", ["tweet_id"], unique=False)
    op.create_index(op.f("ix_likes_user_id"), "likes", ["user_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_likes_user_id"), table_name="likes")
    op.drop_index(op.f("ix_likes_tweet_id"), table_name="likes")
    op.drop_table("likes")
    op.drop_index(op.f("ix_tweets_user_id"), table_name="tweets")
    op.drop_index(op.f("ix_tweets_tweet_id"), table_name="tweets")
    op.drop_table("tweets")
    op.drop_index(op.f("ix_followers_follower_id"), table_name="followers")
    op.drop_index(op.f("ix_followers_followed_id"), table_name="followers")
    op.drop_table("followers")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_images_id"), table_name="images")
    op.drop_table("images")
    # ### end Alembic commands ###
