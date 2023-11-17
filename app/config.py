"""Getting environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Выбор какие сообщения показывать. От подписчиков или все.
tweet_followers: bool = False

# Количество твитов в response.
number_of_tweets: int = 25

# Минимальная и максимальная длина твитов.
max_length_tweet: int = 10_000
min_length_tweet: int = 5

# Допустимые форматы картинок.
allowed_types: tuple = ("image/jpg", "image/png", "image/jpeg")
