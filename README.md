# A simple backend server 

## For run this project follow bellow command

1. Python3 and Pip and Venv Must be installed in your system
2. Now create a virtual environment and active it.
3. Run the command below to install all the packages
   ```
   pip install -r requirements.txt
   ```
4. Make sure you are in right directory and run this command
    First create database named **my_notebook**
    ```
   python3 manage.py makemigrations
   python manage.py migrate
   ```
   _Create database table and migrate all model_
    ```
   python manage.py runserver
   ```
   for start server