from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import role_interactions as ri


@dataclass
class AccountInteractions:
    db_name: str = pod.db_name
    db_user: str = pod.db_user
    db_pass: str = pod.db_pass
    db_host: str = pod.db_host
    db_port: str = pod.db_port

    def __post_init__(self):
        self.connection = pg.connect(database=self.db_name,
                                     user=self.db_user,
                                     password=self.db_pass,
                                     host=self.db_host,
                                     port=self.db_port)

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


if __name__ == "__main__":
    role_interactor = ri.RoleInteractions()

    account_interactor = AccountInteractions()

    roles = role_interactor.get_roles()[0]
    id = roles.role_id

    print('account creation')
    print(account_interactor.create_account(id, "Ada", "Lazi", "adalazi", 'aasd', 111))
    print(account_interactor.create_account(id, "Jess", "Chavi", "jesschavi", 'aasd', 111))
    print(account_interactor.get_account_by_username(user_name="adalazuli"))
    print(account_interactor.get_account_by_id(account_id=2))
    print('account deletion')
    print(account_interactor.delete_account("jesschavi"))
    print(account_interactor.get_account_by_username("jesschavi"))
    print('account locking')
    account = account_interactor.get_account_by_username(user_name="adalazi")
    print(account_interactor.set_account_lock(account_id=account.account_id, locked=True))
    account = account_interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print(account_interactor.set_account_lock(account_id=account.account_id, locked=False))
    account = account_interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print('account log in attempts')
    print(account_interactor.increment_log_in_attempt(account_id=account.account_id))
    account = account_interactor.get_account_by_username(user_name="adalazi")
    print(account)
    print(account_interactor.reset_log_in_attempt(account_id=account.account_id))
    account = account_interactor.get_account_by_username(user_name="adalazi")
    print(account)
