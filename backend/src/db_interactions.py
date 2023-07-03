from dataclasses import dataclass
import psycopg2 as pg
from psycopg2.errorcodes import UNIQUE_VIOLATION
from psycopg2 import errors
import random
import time

from datetime import datetime, timedelta
import hashlib


def generate_code():
    hasher = hashlib.sha512()
    hasher.update(f"{datetime.now()} {random.randint(1, 100000)}".encode())
    return hasher.hexdigest()


    def get_session(self, code, account_id):
        fetched_session = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from sessions where session_code = %(code)s and account_id = %(account_id)s;",
                            {'code': code, 'account_id': account_id})

                fetched_session = cur.fetchone()
            return Session(*fetched_session) if fetched_session is not None else None

        except Exception as e:
            print(e)
            return fetched_session

    def add_session(self, account_id):
        # create code
        code = generate_code()
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO sessions (account_id, creation_date, end_date, session_code) VALUES
                 (%(account_id)s,%(creation_date)s,%(end_date)s,%(session_code)s);""",
                            {'account_id': account_id, 'creation_date': datetime.now(),
                             'end_date': datetime.now() + timedelta(hours=10),
                             'session_code': code})
            return code

        except Exception as e:
            print(e)
            return None

    def add_item(self, account_id, name, description, quantity):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO items (account_id, name, description, quantity, creation_date)
                 VALUES (%(account_id)s,%(name)s,%(description)s,%(quantity)s,%(creation_date)s);""",
                            {'account_id': account_id, 'name': name, 'description': description, 'quantity': quantity,
                             'creation_date': datetime.now()})

            return True

        except Exception as e:
            print(e)
            return None

    def get_item(self, item_id):

        fetched_item = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from items where item_id = %(item_id)s;",
                            {'item_id': item_id})

                fetched_item = cur.fetchone()

            return Item(*fetched_item) if fetched_item is not None else None

        except Exception as e:
            print(e)
            return fetched_item

    def get_items(self):
        fetched_items = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from items;")

                fetched_items = cur.fetchall()

            return [Item(*i) for i in fetched_items]

        except Exception as e:
            print(e)
            return fetched_items

    def delete_item(self, item_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from items where item_id = %(item_id)s;",
                            {'item_id': item_id})

            return True

        except Exception as e:
            print(e)
            return False

    def update_item(self, item_id, name, description, quantity):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""update items SET name = %(name)s, description = %(description)s, 
                quantity = %(quantity)s, modification_date = %(modification_date)s where item_id = %(item_id)s;""",
                            {'name': name, 'description': description, 'quantity': quantity,
                             'modification_date': datetime.now(), 'item_id': item_id})
                return True
        except Exception as e:
            print(e)
            return False

@dataclass
class PermissionChange:
    change_id: int
    account_id: int
    role_id: int
    change_date: datetime


@dataclass
class Session:
    session_id: int
    account_id: int
    creation_date: datetime
    end_date: datetime
    session_code: str


@dataclass
class Annotation:
    annotation_id: int
    observation_id: int
    annotations: str
    creation_date: datetime
    modification_date: datetime


@dataclass
class Observation:
    observation_id: int
    satnogs_id: int
    satellite_name: str
    station_name: str
    status_str: str
    status_code: int
    transmitter: str
    frequency: int
    pull_date: datetime
    original_waterfall: bytes
    greyscale_waterfall: bytes
    threshold_waterfall: bytes


@dataclass
class Task:
    observation_id: int
    status: str
    start: datetime
    completion_date: datetime


if __name__ == "__main__":

    # sessions
    print(f"{'*' * 100}")
    print("SESSIONS")
    account = interactor.get_account_by_username(user_name="adalazi")
    code = interactor.add_session(account.account_id)
    print(f"Created code: {code}")
    print(interactor.get_session(code=code, account_id=id))

    # items
    print(f"{'*' * 100}")
    print("ITEMS")

