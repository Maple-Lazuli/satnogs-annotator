from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import observation_interactions as oi
import model_interactions as mi


@dataclass
class MachineImageInterator:
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

    def create_image(self, model_id, observation_id, waterfall_bytes):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""insert into machine_images (model_id, observation_id, creation_date, waterfall) values
                 (%(model_id)s,%(observation_id)s, %(creation_date)s,%(waterfall_bytes)s);""",
                            {'model_id': model_id,
                             'observation_id': observation_id,
                             'creation_date': datetime.now(),
                             'waterfall_bytes': waterfall_bytes})

            return True

        except Exception as e:
            print(e)
            return False

    def get_image_by_id(self, image_id):
        result = None
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from machine_images where image_id = %(id)s;", {'id': image_id})
                result = cur.fetchone()

            return MachineImage(*result) if result is not None else None
        except Exception as e:
            print(e)
            return result

    def get_images(self):
        fetched_accounts = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from machine_images;")
                fetched_accounts = cur.fetchall()

                return [MachineImage(*a) for a in fetched_accounts]

        except Exception as e:
            print(e)
            return fetched_accounts

    def get_images_by_observation_id(self, observation_id):
        fetched_accounts = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from machine_images where observation_id = %(id)s;", {'id': observation_id})
                fetched_accounts = cur.fetchall()

                return [MachineImage(*a) for a in fetched_accounts]

        except Exception as e:
            print(e)
            return fetched_accounts

    def delete_image(self, image_id):

        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from machine_images where image_id = %(id)s;", {'id': image_id})

            return True

        except Exception as e:
            print(e)
            return False


@dataclass
class MachineImage:
    image_id: int
    model_id: int
    observation_id: int
    creation_date: datetime
    waterfall: bytes


if __name__ == "__main__":
    image_interactor = MachineImageInterator()

    model_interactor = mi.ModelInteractor()
    observation_interactor = oi.ObservationInteractor()

    model = model_interactor.get_models()[0]
    observation = observation_interactor.get_observations()[0]

    print('image creation')
    print(image_interactor.create_image(model_id=model.model_id, observation_id=observation.observation_id,
                                        waterfall_bytes=b"\x00\xff\x11"))
    print(image_interactor.get_images())
    print('image by id')
    image = image_interactor.get_images()[0]
    print(image_interactor.get_image_by_id(image.image_id))
    print(image_interactor.get_images_by_observation_id(observation_id=observation.observation_id))

    print('image deletion')
    print(image_interactor.delete_image(image.image_id))
