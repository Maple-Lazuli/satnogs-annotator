from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import observation_interactions as oi
import model_interactions as mi


def pprint(L):
    for l in L:
        print(l)


@dataclass
class MachineAnnotationInteractor:
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
                cur.execute(f"select * from machine_annotations where annotation_id = %(annotation_id)s;",
                            {'annotation_id': annotation_id})

                fetched_annotation = cur.fetchone()

            return MachineAnnotation(*fetched_annotation) if fetched_annotation is not None else None

        except Exception as e:
            print(e)
            return fetched_annotation

    def get_annotations_by_observation_id(self, observation_id):
        fetched_annotations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from machine_annotations where observation_id = %(observation_id)s;",
                            {'observation_id': observation_id})

                fetched_annotations = cur.fetchall()

            return [MachineAnnotation(*i) for i in fetched_annotations]

        except Exception as e:
            print(e)
            return fetched_annotations

    def get_annotations(self):
        fetched_annotations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from machine_annotations;")

                fetched_annotations = cur.fetchall()

            return [MachineAnnotation(*i) for i in fetched_annotations]

        except Exception as e:
            print(e)
            return fetched_annotations

    def delete_annotation(self, annotation_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from machine_annotations where annotation_id = %(annotation_id)s;",
                            {'annotation_id': annotation_id})

            return True

        except Exception as e:
            print(e)
            return False

    def add_annotation(self, model_id, observation_id, x_center, y_center, width, height):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO machine_annotations (model_id, observation_id, creation_date, x_center, y_center,
                 width, height) VALUES (%(model_id)s, %(observation_id)s,%(creation_date)s,%(x_center)s,%(y_center)s,
                 %(width)s,%(height)s);""",
                            {'model_id': model_id, 'observation_id': observation_id,
                             'creation_date': datetime.now(),
                             'x_center': x_center, 'y_center': y_center, 'width': width, 'height': height})
            return True

        except Exception as e:
            print(e)
            return None


@dataclass
class MachineAnnotation:
    annotation_id: int
    model_id: int
    observation_id: int
    creation_date: datetime
    x_center: float
    y_center: float
    width: float
    height: float


if __name__ == "__main__":
    model_interactor = mi.ModelInteractor()
    observation_interactor = oi.ObservationInteractor()

    machine_annotation_interactor = MachineAnnotationInteractor()

    print("\nAdding An Annotation")

    model = model_interactor.get_models()[0]
    observation = observation_interactor.get_observations()[0]

    machine_annotation_interactor.add_annotation(model_id=model.model_id, observation_id=observation.observation_id,
                                                 x_center=0.5, y_center=.2, width=.1, height=.6)

    pprint(machine_annotation_interactor.get_annotations())

    print("\nDeleting An Annotation")
    annotation = machine_annotation_interactor.get_annotations()[0]
    print(machine_annotation_interactor.delete_annotation(annotation_id=annotation.annotation_id))

