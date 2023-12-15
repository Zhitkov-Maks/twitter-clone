"""Getting environment variables, as well as some application settings."""
import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Выбор какие сообщения показывать. От подписчиков или все.
tweet_followers: bool = False

# Количество твитов в response.
number_of_tweets: int = 100

# Минимальная и максимальная длина твитов. Если меняете, то нужно выполнить миграции.
max_length_tweet: int = 10_000
min_length_tweet: int = 5

# Допустимые форматы картинок, если хотите добавить допустим формат gif,
# то нужно отредактировать nginx.conf (jpeg|png|jpg|webp|gif)
allowed_types: tuple = ("image/jpg", "image/png", "image/jpeg", "image/webp")
