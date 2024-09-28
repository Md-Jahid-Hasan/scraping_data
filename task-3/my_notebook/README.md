# A simple backend server named my_notebook

## Database requirements
Make sure you have postgresql installed in your system and create a database named **my_notebook**.
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
    First create database named **my_notebook**
    ```
   python3 manage.py makemigrations
   python manage.py migrate
   ```
   _Above command create database table and migrate all model_
   
   Now create a superuser for initial login(Not mandatory)
    ```
   python manage.py createsuperuser
   ```
   
5. Now run this command to start development server
    ```
   python manage.py runserver
   ```

## API endpoint details
   1. **POST** /api/user/login/ - For login user
       
      ```
      body: {
        "email": "",
        "password": ""
      }
      ```
   2. **POST** /api/user/create/ - For register user
       
      ```
      body:{
        "name": "",
        "email": "",
        "password": "",
        "confirm_password": "",
      }
      ```
   3. **GET** /api/user/ - For retrieve current log in user
   4. **POST** /api/notebook/ - For create notebook
      ```
      body: {
        "title": "",
        "description": "",
        "category": ""  #id of category
      }
      ```
   5. **GET** /api/notebook/ - For retrieve all notebook
   6. **GET** /api/notebook/{id}/ - For retrieve single notebook
   7. **PUT/PATCH** /api/notebook/{id}/ - For update single notebook
      
      ```
      body: {
        "title": "",
        "description": "",
        "category": ""  #id of category
      }
      ```
   8. **DELETE** /api/notebook/{id}/ - For delete single notebook
   9. **POST** /api/notebook/category/ - For create notebook category
        ```
        body: {
            "name": ""
        }
        ```
   10. **GET** /api/notebook/category/ - For retrieve all notebook category