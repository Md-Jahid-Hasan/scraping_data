# My Notebook - A Simple Backend Server
This is a Django-based backend server for managing user accounts and notebooks. 
The project includes functionalities such as user registration, login, and notebook creation, 
updating, and deletion. All data is stored in a PostgreSQL database.

## Database Requirements
1. Ensure PostgreSQL is installed on your system.
2. Create a database named `my_notebook`.
3. Create a `.env` file in the root directory with the following configuration:
    ```
    PGUSER={{postgres_username}}
    PASSWORD={{postgres_password}}
    ```

# Project Setup
### Prerequisites
* Python3 and Pip and Venv Must be installed in your system

### Setup Instructions
1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment:
    ```
    virtualenv venv
    ```
   active for ubuntu
    ```
    source venv/bin/activate
    ```
    active for windows
    ```
    venv\Scripts\activate
    ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database:
    * Ensure the PostgreSQL database named `my_notebook` has been created.
    * Run the following commands to create the database tables and apply migrations:
       ```
       python3 manage.py makemigrations
       python manage.py migrate
       ```
   _These commands will create the necessary database tables and apply all model migrations._
   
5. (Optional) Create a superuser for initial admin login:
    ```
   python manage.py createsuperuser
   ```
6. Run the development server:
    ```
   python manage.py runserver
   ```

## API endpoint details
Here are the available API endpoints for user management and notebook functionality:

### User Management
   1. **POST** `/api/user/login/` - For login user
       
      ```
      body: {
        "email": "",
        "password": ""
      }
      ```
   2. **POST** `/api/user/create/` - For register user
       
      ```
      body:{
        "name": "",
        "email": "",
        "password": "",
        "confirm_password": "",
      }
      ```
   3. **GET** `/api/user/` - For retrieve current log in user
### Notebook Management
   1. **POST** /api/notebook/ - For create notebook
      ```
      body: {
        "title": "",
        "description": "",
        "category": ""  #id of category
      }
      ```
   2. **GET** `/api/notebook/` - For retrieve all notebook
   3. **GET** `/api/notebook/{id}/` - For retrieve single notebook
   4. **PUT/PATCH** `/api/notebook/{id}/` - For update single notebook
      ```
      body: {
        "title": "",
        "description": "",
        "category": ""  #id of category
      }
      ```
   5. **DELETE** `/api/notebook/{id}/` - For delete single notebook
### Notebook Category Management
   1. **POST** `/api/notebook/category/` - For create notebook category
        ```
        body: {
            "name": ""
        }
        ```
   2. **GET** `/api/notebook/category/` - For retrieve all notebook category