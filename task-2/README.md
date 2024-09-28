# Web Scraper for scrape a specific source

## Database requirements
Make sure you have postgresql installed in your system and create a database named **backend_interview**.
Now create a .env file in the root directory and add the following lines
```
PGUSER={postgres_username}
PASSWORD={postgres_password}
```

## For run this project follow bellow command

1. Python3 and Pip and Venv Must be installed in your system
2. Now create a virtual environment and active it.
3. Run the command below to install all the packages
   ```
   pip install -r requirements.txt
   ```
4. Make sure you are in right directory and run this command
    ```
   python3 scraper.py
   ```
   for ubuntu
    ```
   python scraper.py
   ```
   for windows