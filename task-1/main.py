from scraper import Scraper
from download_file import DownloadFile

if __name__ == "__main__":
    local_download = DownloadFile()
    scraper = Scraper(local_download)
