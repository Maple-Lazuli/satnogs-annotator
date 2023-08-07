from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod


@dataclass
class ModelInteractor:
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

    def create_model(self, model_name, description):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""insert into models (model_name, creation_date, description) values (%(model_name)s,
                %(creation_date)s,%(description)s);""", {'model_name': model_name, 'creation_date': datetime.now(),
                                                         'description': description})

            return True

        except Exception as e:
            print(e)
            return False

    def get_model_by_id(self, model_id):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from models where model_id = %(id)s;", {'id': model_id})
                result = cur.fetchone()

            return Model(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def get_model_by_name(self, name):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from models where model_name = %(id)s;", {'id': name})
                result = cur.fetchone()

            return Model(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def get_models(self):
        fetched_accounts = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from models;")
                fetched_accounts = cur.fetchall()

                return [Model(*a) for a in fetched_accounts]

        except Exception as e:
            print(e)
            return fetched_accounts

    def delete_model(self, model_id):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from models where model_id = %(id)s;", {'id': model_id})

            return True

        except Exception as e:
            print(e)
            return False


@dataclass
class Model:
    model_id: int
    model_name: str
    creation_date: datetime
    description: str


if __name__ == "__main__":
    model_interactor = ModelInteractor()
    print('model creation')
    print(model_interactor.create_model("Model1", "A nonexistent model for testing"))
    print(model_interactor.create_model("Model2", "A second nonexistent model for testing"))
    print(model_interactor.get_models())
    print('get model by name')
    model = model_interactor.get_model_by_name("Model1")
    print(model)
    print('model deletion')
    print(model_interactor.delete_model(model.model_id))
