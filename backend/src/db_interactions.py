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


@dataclass
class DBInteractions:
    db_name: str = 'inventory_db'
    db_user: str = 'postgres'
    db_pass: str = 'postgres'
    db_host: str = 'postgres'
    db_port: str = '5432'

    def __post_init__(self):
        time.sleep(10)
        self.connection = pg.connect(database=self.db_name,
                                     user=self.db_user,
                                     password=self.db_pass,
                                     host=self.db_host,
                                     port=self.db_port)

    def create_new_role(self, role_name):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute("insert into roles (role_name) values (%(r)s);", {'r': role_name})

            return True

        except errors.lookup(UNIQUE_VIOLATION) as e:
            print(e)
            return False

        except Exception as e:
            print(e)
            return False

    def get_roles(self):
        fetched_roles = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from roles;")
                fetched_roles = cur.fetchall()

            return [Role(*r) for r in fetched_roles]

        except Exception as e:
            print(e)
            return fetched_roles

    def get_role(self, role_id):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from roles where role_id = %(u)s;", {'u': role_id})
                result = cur.fetchone()
            return Role(*result) if result is not None else None

        except Exception as e:
            print(e)
            return None

    def get_role_by_name(self, role_name):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from roles where role_name = %(name)s;", {'name': role_name})
                result = cur.fetchone()

            return Role(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def create_account(self, role_id, first_name, last_name, user_name, password, salt):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""insert into accounts (role_id, first_name, last_name, created_on, username, password,
                    salt, locked, log_in_attempts) values (%(role_id)s,%(first_name)s,%(last_name)s,%(created_on)s,
                    %(username)s,%(password)s,%(salt)s,%(locked)s,%(log_ins)s);""", {'role_id': role_id,
                                                                                     'first_name': first_name,
                                                                                     'last_name': last_name,
                                                                                     'username': user_name,
                                                                                     'password': password,
                                                                                     'created_on': datetime.now(),
                                                                                     'salt': salt, 'locked': False,
                                                                                     'log_ins': 0})

            return True

        except Exception as e:
            print(e)
            return False

    def update_account(self, account_id, first_name, last_name, user_name, password):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""update accounts SET first_name = %(first_name)s, last_name = %(last_name)s,
                 username = %(username)s, password = %(password)s where account_id = %(account_id)s;""",
                            {'account_id': account_id, 'first_name': first_name, 'last_name': last_name,
                             'username': user_name, 'password': password})

            return True


        except Exception as e:
            print(e)
            return False

    def get_account_by_id(self, account_id):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from accounts where account_id = %(id)s;", {'id': account_id})
                result = cur.fetchone()

            return Account(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def get_account_by_username(self, user_name):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from accounts where username = %(id)s;", {'id': user_name})
                result = cur.fetchone()

            return Account(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def get_accounts(self):
        fetched_accounts = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from accounts;")
                fetched_accounts = cur.fetchall()

                return [Account(*a) for a in fetched_accounts]

        except Exception as e:
            print(e)
            return fetched_accounts

    def delete_account(self, user_name):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from accounts where username = %(u)s;", {'u': user_name})

            return True

        except Exception as e:
            print(e)
            return False

    def set_account_lock(self, account_id, locked):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"update accounts SET locked = %(locked)s where account_id = %(account_id)s;",
                            {'locked': locked, 'account_id': account_id})
        except Exception as e:
            print(e)
            return False

    def increment_log_in_attempt(self, account_id):
        account = self.get_account_by_id(account_id)
        log_in_attempts = account.log_in_attempts + 1
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(
                    f"update accounts SET log_in_attempts = %(log_in_attempts)s where account_id = %(account_id)s;",
                    {'log_in_attempts': log_in_attempts, 'account_id': account_id})
            return True

        except Exception as e:
            print(e)
            return False

    def reset_log_in_attempt(self, account_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(
                    f"update accounts SET log_in_attempts = %(log_in_attempts)s where account_id = %(account_id)s;",
                    {'log_in_attempts': 0, 'account_id': account_id})
            return True

        except Exception as e:
            print(e)
            return False

    def update_permissions(self, role_id, account_id):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"update accounts SET role_id = %(role_id)s where account_id = %(account_id)s;",
                            {'role_id': role_id, 'account_id': account_id})
        except Exception as e:
            print(e)
            return False

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO permission_changes (account_id, role_id, change_date) VALUES
                             (%(account_id)s,%(role_id)s,%(change_date)s);""",
                            {'account_id': account_id, 'role_id': role_id, 'change_date': datetime.now()})

        except Exception as e:
            print(e)
            return False

        return True

    def get_permission_changes(self):
        results = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from permission_changes;")
                results = cur.fetchall()
            return [PermissionChange(*pc) for pc in results]

        except Exception as e:
            print(e)
            return results

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
class Role:
    role_id: int
    role_name: str


@dataclass
class Account:
    account_id: int
    role_id: int
    first_name: str
    last_name: str
    created_on: datetime
    user_name: str
    password: str
    salt: int
    locked: bool
    log_in_attempts: int


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
    interactor = DBInteractions()

    # Roles
    print(f"{'*' * 100}")
    print("ROLES")
    print(interactor.get_roles())
    print(interactor.create_new_role("Administrator"))
    print(interactor.create_new_role("Manager"))

    print(interactor.get_roles())

    # Accounts
    print(f"{'*' * 100}")
    print("ACCOUNTS")
    roles = interactor.get_roles()[0]
    id = roles.role_id
    print(interactor.create_account(id, "Ada", "Lazi", "adalazi", 'aasd', 111))
    print(interactor.create_account(id, "Jess", "Chavi", "jesschavi", 'aasd', 111))
    print(interactor.get_account_by_username(user_name="adalazuli"))
    print(interactor.get_account_by_id(account_id=2))
    print('delete')
    print(interactor.delete_account("jesschavi"))
    print(interactor.get_account_by_username("jesschavi"))
    account = interactor.get_account_by_username(user_name="adalazi")
    print(interactor.set_account_lock(account_id=account.account_id, locked=True))
    account = interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print(interactor.set_account_lock(account_id=account.account_id, locked=False))
    account = interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print(interactor.increment_log_in_attempt(account_id=account.account_id))
    account = interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print(interactor.reset_log_in_attempt(account_id=account.account_id))
    account = interactor.get_account_by_username(user_name="adalazi")
    print(account)

    # permissions
    print(f"{'*' * 100}")
    print("PERMISSION CHANGES")
    roles = interactor.get_roles()[1]
    id = roles.role_id
    account = interactor.get_account_by_username(user_name="adalazi")
    print(interactor.get_permission_changes())
    print(interactor.update_permissions(role_id=id, account_id=account.account_id))
    print(interactor.get_permission_changes())
    print(interactor.get_account_by_id(account_id=account.account_id))

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

