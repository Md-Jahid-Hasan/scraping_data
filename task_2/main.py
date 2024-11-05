from scraper import Scraper
from db import Database

if __name__ == "__main__":
    db = Database()
    scraper = Scraper(db)