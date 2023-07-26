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

    def update_annotation(self, annotation_id, x0, y0, x1, y1,
                       image_width, image_height):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""update annotations SET x0 = %(x0)s, y0 = %(y0)s, x1 = %(x1)s, y1 = %(y1)s, 
                annotation_height = %(annotation_height)s, annotation_width = %(annotation_width)s,
                 image_width = %(image_width)s, image_height = %(image_height)s
                 where annotation_id = %(annotation_id)s;""",
                            {'annotation_id': annotation_id,
                             'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'annotation_width': x1 - x0,
                             'annotation_height': y1 - y0, 'image_width': image_width,
                             'image_height': image_height})
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

    def add_annotation(self, account_id, observation_id, x0, y0, x1, y1,
                       image_width, image_height):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO annotations (account_id, observation_id, creation_date, x0, y0, x1, y1,
                annotation_width, annotation_height, image_width, image_height) VALUES (%(account_id)s,
                %(observation_id)s,%(creation_date)s,%(x0)s,%(y0)s,%(x1)s,%(y1)s,%(annotation_width)s,
                %(annotation_height)s,%(image_width)s,%(image_height)s);""",
                            {'account_id': account_id, 'observation_id': observation_id,
                             'creation_date': datetime.now(),
                             'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1, 'annotation_width': x1 - x0,
                             'annotation_height': y1 - y0, 'image_width': image_width,
                             'image_height': image_height})
            return True

        except Exception as e:
            print(e)
            return None


@dataclass
class Annotation:
    annotation_id: int
    account_id: int
    observation_id: int
    creation_date: datetime
    x0: float
    y0: float
    x1: float
    y1: float
    annotation_width: float
    annotation_height: float
    image_width: float
    image_height: float



if __name__ == "__main__":
    account_interactor = ai.AccountInteractor()
    observation_interactor = oi.ObservationInteractor()

    annotation_interactor = AnnotationInteractor()

    print("\nGetting Annotations")

    print(annotation_interactor.get_annotations())

    print("\nAdding An Annotation")

    account_id = account_interactor.get_accounts()[0].account_id
    observation_id = observation_interactor.get_observations()[0].observation_id

    print(f"Account_id:{account_id} and Observation_id:{observation_id}")

    annotation_interactor.add_annotation(account_id=account_id, observation_id=observation_id, x0=0, y0=0, x1=1, y1=1,
                                         image_width=1, image_height=1)

    pprint(annotation_interactor.get_annotations())

    print("\nUpdating An Annotation")

    annotation_id = annotation_interactor.get_annotation_by_account_and_observation(account_id=account_id,
                                                                                    observation_id=observation_id).annotation_id

    annotation_interactor.update_annotation(annotation_id=annotation_id, x0=0, y0=0, x1=.5, y1=.5, image_width=1,
                                            image_height=1)

    pprint(annotation_interactor.get_annotations())
