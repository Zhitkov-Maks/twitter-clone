"""Deleting pictures when deleting a tweet."""
import os
from pathlib import Path
from typing import List


OUT_PATH = Path(__file__).parent.parent / "./dist/images"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


async def remove_images(images_list: List[str]) -> None:
    """
    Функция для удаления картинок из хранилища.

    :param images_list: Список имен картинок которые необходимо удалить.
    :return: None
    """
    for img in images_list:
        os.remove(f"{OUT_PATH}/{img}")
