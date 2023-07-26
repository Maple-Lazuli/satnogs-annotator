from dataclasses import dataclass
from datetime import datetime, timedelta

import psycopg2 as pg

import postgres_defaults as pod
import account_interactions as ai

@dataclass
class SessionInteractor:
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
        code = pod.generate_code()
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


@dataclass
class Session:
    session_id: int
    account_id: int
    creation_date: datetime
    end_date: datetime
    session_code: str


if __name__ == "__main__":
    account_interactor = ai.AccountInteractor()
    session_interactor = SessionInteractor()

    account_id = account_interactor.get_account_by_username(user_name='adalazi').account_id

    code = session_interactor.add_session(account_id)
    print(f"Created code: {code}")
    print(session_interactor.get_session(code=code, account_id=account_id))
