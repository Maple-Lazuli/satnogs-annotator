from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import observation_interactions as oi
import account_interactions as ai


def pprint(L):
    for l in L:
        print(l)


@dataclass
class AnnotationInteractor:
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

    def get_annotation(self, annotation_id):
        fetched_annotation = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from annotations where annotation_id = %(annotation_id)s;",
                            {'annotation_id': annotation_id})

                fetched_annotation = cur.fetchone()

            return Annotation(*fetched_annotation) if fetched_annotation is not None else None

        except Exception as e:
            print(e)
            return fetched_annotation

    def get_annotation_by_account_and_observation(self, account_id, observation_id):
        fetched_annotation = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""select * from annotations where account_id = %(account_id)s and
                                observation_id = %(observation_id)s;""",
                            {'account_id': account_id, 'observation_id': observation_id})

                fetched_annotation = cur.fetchone()

            return Annotation(*fetched_annotation) if fetched_annotation is not None else None

        except Exception as e:
            print(e)
            return fetched_annotation

    def get_annotations_by_account_id(self, account_id):
        fetched_annotations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from annotations where account_id = %(account_id)s;",
                            {'account_id': account_id})

                fetched_annotations = cur.fetchall()

            return [Annotation(*i) for i in fetched_annotations]

        except Exception as e:
            print(e)
            return fetched_annotations

    def get_annotations_by_observation_id(self, observation_id):
        fetched_annotations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from annotations where observation_id = %(observation_id)s;",
                            {'observation_id': observation_id})

                fetched_annotations = cur.fetchall()

            return [Annotation(*i) for i in fetched_annotations]

        except Exception as e:
            print(e)
            return fetched_annotations

    def get_annotations(self):
        fetched_annotations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from annotations;")

                fetched_annotations = cur.fetchall()

            return [Annotation(*i) for i in fetched_annotations]

        except Exception as e:
            print(e)
            return fetched_annotations

    def update_annotation(self, annotation_id, upper_left, lower_right):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""update annotations SET upper_left = %(upper_left)s, lower_right = %(lower_right)s, 
                 modification_date = %(modification_date)s where annotation_id = %(annotation_id)s;""",
                            {'annotation_id': annotation_id, 'upper_left': upper_left, 'lower_right': lower_right,
                             'modification_date': datetime.now()})
                return True
        except Exception as e:
            print(e)
            return False

    def delete_annotation(self, annotation_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from annotations where annotation_id = %(annotation_id)s;",
                            {'annotation_id': annotation_id})

            return True

        except Exception as e:
            print(e)
            return False

    def add_annotation(self, account_id, observation_id, upper_left, lower_right):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO annotations (account_id, observation_id, upper_left, lower_right, creation_date)
                 VALUES (%(account_id)s,%(observation_id)s,%(upper_left)s,%(lower_right)s,%(creation_date)s);""",
                            {'account_id': account_id, 'observation_id': observation_id, 'upper_left': upper_left,
                             'lower_right': lower_right, 'creation_date': datetime.now()})
            return True

        except Exception as e:
            print(e)
            return None


@dataclass
class Annotation:
    annotation_id: int
    account_id: int
    observation_id: int
    upper_left: list
    lower_right: list
    creation_date: datetime
    modification_date: datetime


if __name__ == "__main__":
    account_interactor = ai.AccountInteractions()
    observation_interactor = oi.ObservationInteractor()

    annotation_interactor = AnnotationInteractor()

    print("\nGetting Annotations")

    print(annotation_interactor.get_annotations())

    print("\nAdding An Annotation")

    account_id = account_interactor.get_accounts()[0].account_id
    observation_id = observation_interactor.get_observations()[0].observation_id

    print(f"Account_id:{account_id} and Observation_id:{observation_id}")

    annotation_interactor.add_annotation(account_id=account_id, observation_id=observation_id, upper_left=[1, 2, 3],
                                         lower_right=[5, 6, 7])

    pprint(annotation_interactor.get_annotations())

    print("\nUpdating An Annotation")

    annotation_id = annotation_interactor.get_annotation_by_account_and_observation(account_id=account_id,
                                                            observation_id=observation_id).annotation_id

    annotation_interactor.update_annotation(annotation_id=annotation_id, upper_left=[9, 8, 7], lower_right=[1, 4, 8])

    pprint(annotation_interactor.get_annotations())
