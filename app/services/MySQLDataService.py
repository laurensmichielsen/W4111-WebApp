import os

from .AbstractBaseDataService import AbstractBaseDataService
import mysql
from mysql.connector import errorcode
from dotenv import load_dotenv
from typing import List

# TODO: decide the table based on the config
# we use the table in the queries: pretty simple stuff and that way we can reuse the MySQLDataService
class MySQLDataService(AbstractBaseDataService):

    def __init__(self, config):
        # Method based on 
        # https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
        super().__init__(config)
        load_dotenv()

        DB_HOST = os.getenv("DB_HOST")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        DB_PORT = os.getenv("DB_PORT", 3306)
        try:
            cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, 
                                          host=DB_HOST, database=DB_NAME, port=DB_PORT)

        except mysql.connector.Error as err:
            print("Error")
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            print("Connected")
            # store the connection and create a cursor for the session
            self.connection = cnx
            self.cursor = cnx.cursor(dictionary=True, buffered=True)

            self.table = str(config["table"])
    
    def close_connection(self):
        # if the connection still exists close it
        if self.connection:
            self.connection.close()
            print("Connection closed")

    def _build_where_clause(self, primary_key: dict):
        values = [value for value in primary_key.values()]

        conditions = [f"{f} = %s" for f in primary_key.keys()]
        where_clause = " AND ".join(conditions)

        return f"WHERE {where_clause}", tuple(values)

    def retrieveByPrimaryKey(self, primary_key: dict) -> dict:
        where_clause, values = self._build_where_clause(primary_key)
        query = (
            f"SELECT * FROM {self.table} "
            f"{where_clause}"
        )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return dict(result) if result else {}

    def retrieveByTemplate(self, template: dict) -> list[dict]:
        if not template:
            query = f"SELECT * FROM {self.table}"
            self.cursor.execute(query)
            return self.cursor.fetchall()

        conditions = [f"{key} = %s" for key in template.keys()]
        where_clause = " AND ".join(conditions)

        query = f"SELECT * FROM {self.table} WHERE {where_clause}"

        self.cursor.execute(query, tuple(template.values()))
        return self.cursor.fetchall()

    # TODO: check if pk already exists
    def create(self, payload: dict, primary_key: dict) -> int:
        if not payload:
            return None
        
        row_key = self.retrieveByPrimaryKey(primary_key)
        if row_key:
            raise ValueError("Record with key does already exist")

        columns = ", ".join(payload.keys())
        placeholders = ", ".join(["%s"] * len(payload))

        query = f"""
            INSERT INTO {self.table} ({columns})
            VALUES ({placeholders})
        """

        values = tuple(payload.values())

        self.cursor.execute(query, values)
        self.connection.commit()

        # return primary key if available
        return self.cursor.lastrowid


    # if PK exists: 1
    # else 0
    def updateByPrimaryKey(self, primary_key: dict, payload: dict) -> int:
        if not payload:
            return 0
        row_key = self.retrieveByPrimaryKey(primary_key)
        if not row_key:
            return 0
        
        set_clause = ", ".join([f"{key} = %s" for key in payload.keys()])
        where_clause, key_values = self._build_where_clause(primary_key)

        query = f"""
            UPDATE {self.table}
            SET {set_clause}
            {where_clause}
        """

        values = tuple(payload.values()) + key_values

        self.cursor.execute(query, values)
        self.connection.commit()

        print("Rows updated:", self.cursor.rowcount)
        return self.cursor.rowcount

    def deleteByPrimaryKey(self, primary_key: dict) -> int:
        row_key = self.retrieveByPrimaryKey(primary_key)
        if not row_key:
            raise ValueError("Record with key does not exist")
        where_clause, values = self._build_where_clause(primary_key)
        query = f"""
            DELETE FROM {self.table}
            {where_clause}
        """

        self.cursor.execute(query, values)
        self.connection.commit()

        return self.cursor.rowcount
    
