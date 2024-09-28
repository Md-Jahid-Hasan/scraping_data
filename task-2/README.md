# Web Scraper for a Specific Source
This script(`scraper.py`) is designed to scrape data from a specified source and store it in a PostgreSQL database

## Database Requirements
Ensure PostgreSQL is installed on your system and create a database named **backend_interview**.
Then, create a `.env` file in the root directory and add the following lines:
```
PGUSER={postgres_username}
PASSWORD={postgres_password}
```

# Project Setup
## Prerequisites

1. Python 3, pip, and virtualenv must be installed on your system.
2. Create a virtual environment and activate it:<br>
   Create a virtual environment -
    ```
    virtualenv venv
    ```
   Activate the virtual environment - <br>
   for ubuntu
    ```
    source venv/bin/activate
    ```
   for windows
    ```
    venv\Scripts\activate
    ```
3. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```
4. Ensure you are in the correct directory and execute the scraper script:

   for ubuntu
   ```
   python3 scraper.py
   ```
   for windows
    ```
   python scraper.py
   ```
   