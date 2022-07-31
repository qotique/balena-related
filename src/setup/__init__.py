from src.rm_guide import RickAndMortyGuide
from src.config import DB_URL
from db.engine import DataBase


def setup():
    database = DataBase(DB_URL)
    app = RickAndMortyGuide()


if __name__ == '__main__':
    setup()
