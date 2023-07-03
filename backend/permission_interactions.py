from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import account_interactions as ai
import role_interactions as ri


@dataclass
class PermissionInteractions:
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


@dataclass
class PermissionChange:
    change_id: int
    account_id: int
    role_id: int
    change_date: datetime


if __name__ == "__main__":

    account_interactor = ai.AccountInteractions()
    role_interactor = ri.RoleInteractions()
    permission_interactor = PermissionInteractions()

    role_id = role_interactor.get_roles()[1].role_id
    account_id = account_interactor.get_account_by_username(user_name="adalazi").account_id

    print(permission_interactor.get_permission_changes())
    print(permission_interactor.update_permissions(role_id=role_id, account_id=account_id))
    print(permission_interactor.get_permission_changes())
    print(account_interactor.get_account_by_id(account_id=account_id))
