import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()


class Database:
    def __init__(self):
        self.connection = self.connect()
        if self.connection:
            self.create_tables_if_not_exists()
    def connect(self):
        """This method is responsible for connecting to the database."""
        try:
            connection = psycopg2.connect(
                database='backend_interview',host='localhost',port='5432',
                user=os.getenv('PGUSER'),password=os.getenv('PASSWORD')
            )
            print("Connected to PostgreSQL")

            return connection
        except psycopg2.Error as e:
            print(f"Failed to connect to database: {e}")
            input("Please create a database named 'backend_interview' and press enter to retry.....")
            self.connect()

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def create_tables_if_not_exists(self):
        try:
            if not self.connection:
                self.connection = self.connect()

            cursor = self.connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS data_info (id serial primary key, folder varchar(10) not null,"
                           "sample text not null, result varchar(100) not null);")
            self.connection.commit()

            cursor.execute("CREATE TABLE IF NOT EXISTS result_data (id serial primary key, name varchar(100), tax_id varchar(100),"
                           "accession_id varchar(100), class varchar(100), relative_abundance varchar(50), abundance_score varchar(50),"
                           "total_matches varchar(50), unique_matches varchar(50), unique_matches_frequency varchar(100),"
                           "data_info integer, CONSTRAINT result_data_info FOREIGN KEY(data_info) REFERENCES data_info(id));")
            self.connection.commit()

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS taxonomy_data (id serial primary key, name varchar(100), tax_id varchar(50),"
                "relative_abundance varchar(50), abundance_score varchar(50), unique_matches_frequency varchar(50),"
                "data_info integer, CONSTRAINT taxonomy_data_info FOREIGN KEY(data_info) REFERENCES data_info(id));")
            self.connection.commit()

            self.connection.close()
        except Exception as e:
            print(f"Failed to create table because: {str(e)}")
    
    def save_result_data(self, data, folder, sample_name, result_name):
        if not self.connection:
            self.connection = self.connect()
        cursor = self.connection.cursor()
        data_info = self.get_or_create_data_info(folder, sample_name, result_name)
        if data_info:
            for row in data[1:]:
                try:
                    row.append(data_info)
                    if len(row) == 9:
                        cursor.execute("INSERT INTO result_data (name, accession_id, class, relative_abundance, abundance_score, "
                                       "total_matches, unique_matches,unique_matches_frequency, data_info) VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s)", tuple(row))
                    else:
                        cursor.execute(
                            "INSERT INTO result_data (name, tax_id, relative_abundance, abundance_score, "
                            "total_matches, unique_matches,unique_matches_frequency, data_info) VALUES (%s,%s,%s,%s,%s,%s, %s, %s)",
                            tuple(row))

                    self.connection.commit()
                except Exception as e:
                    print(f"Failed to save data for {folder}/{sample_name}/{result_name} because: {str(e)}")

    def save_taxonomy_data(self, data, folder, sample_name, key):
        if not self.connection:
            self.connection = self.connect()
        cursor = self.connection.cursor()
        data_info = self.get_or_create_data_info(folder, sample_name, key)

        if data_info:
            for row in data:
                try:
                    cursor.execute("INSERT INTO taxonomy_data (name, tax_id, relative_abundance, abundance_score, "
                                   "unique_matches_frequency, data_info) VALUES (%s,%s,%s,%s,%s,%s)",
                                   (row['name'],row['tax_id'],row['relative_abundance'],row['abundance_score'],
                                    row['hit_frequency'],data_info))
                    self.connection.commit()
                except Exception as e:
                    print(f"Failed to save data for {folder}/{sample_name}/{key} because {str(e)}")

    def get_or_create_data_info(self, folder, sample_name, result):
        if not self.connection:
            self.connection = self.connect()
        cursor = self.connection.cursor()

        try:
            cursor.execute("SELECT id FROM data_info WHERE folder = %s AND sample = %s AND result = %s",
                           (folder, sample_name, result))
            data_info = cursor.fetchone()

            if not data_info:
                cursor.execute("INSERT INTO data_info (folder, sample, result) VALUES (%s, %s, %s) RETURNING id",
                               (folder, sample_name, result))
                data_info = cursor.fetchone()
                self.connection.commit()
            return data_info[0]
        except Exception as e:
            print(f"Failed to save or get data_info for {folder}/{sample_name}/{result} because: {str(e)}")
            return None


Database()