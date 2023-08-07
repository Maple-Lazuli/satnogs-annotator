from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import satnogs_interactions as si

@dataclass
class ObservationInteractor:
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

    def add_observation(self, satnogs_id, satellite_name, station_name, status, status_code, transmitter, frequency,
                        original_waterfall, greyscaled_waterfall, thresholded_waterfall, length, width):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""INSERT INTO observations (satnogs_id, satellite_name, station_name, status, status_code,
                transmitter, frequency, pull_date, original_waterfall, greyscaled_waterfall, thresholded_waterfall, 
                waterfall_length, waterfall_width) values (%(satnogs_id)s, %(satellite_name)s, %(station_name)s,
                 %(status)s, %(status_code)s, %(transmitter)s, %(frequency)s, %(pull_date)s, %(original_waterfall)s,
                  %(greyscaled_waterfall)s, %(thresholded_waterfall)s, %(waterfall_length)s, %(waterfall_width)s);""",
                            {'satnogs_id': satnogs_id, 'satellite_name': satellite_name,
                             'station_name': station_name, 'status': status,
                             'status_code': status_code,
                             'transmitter': transmitter, 'frequency': frequency,
                             'pull_date': datetime.now(),
                             'original_waterfall': original_waterfall,
                             'greyscaled_waterfall': greyscaled_waterfall,
                             'thresholded_waterfall': thresholded_waterfall,
                             'waterfall_length': length,
                             'waterfall_width': width})
                return True

        except Exception as e:
            print(e)
            return None

    def get_observation(self, observation_id):

        fetched_observation = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from observations where observation_id = %(observation_id)s;",
                            {'observation_id': observation_id})

                fetched_observation = cur.fetchone()

            return Observation(*fetched_observation) if fetched_observation is not None else None

        except Exception as e:
            print(e)
            return fetched_observation

    def get_observation_by_satnogs_id(self, satnogs_id):

        fetched_observation = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from observations where satnogs_id = %(satnogs_id)s;",
                            {'satnogs_id': satnogs_id})

                fetched_observation = cur.fetchone()

            return Observation(*fetched_observation) if fetched_observation is not None else None

        except Exception as e:
            print(e)
            return fetched_observation

    def get_observations(self):
        fetched_observations = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from observations;")

                fetched_items = cur.fetchall()

            return [Observation(*i) for i in fetched_items]

        except Exception as e:
            print(e)
            return fetched_observations

    def delete_observation(self, observation_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"delete from observations where observation_id = %(observation_id)s;",
                            {'observation_id': observation_id})

            return True

        except Exception as e:
            print(e)
            return False

    def update_observation(self, observation_id, satnogs_id, satellite_name, station_name, status, status_code,
                           transmitter, frequency,
                           original_waterfall, greyscaled_waterfall, thresholded_waterfall, length, width):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""update observations SET satnogs_id = %(satnogs_id)s, satellite_name = %(satellite_name)s,
                 station_name = %(station_name)s, status = %(status)s, status_code = %(status_code)s,
                  transmitter = %(transmitter)s, frequency = %(frequency)s, pull_date = %(pull_date)s,
                   original_waterfall = %(original_waterfall)s, greyscaled_waterfall = %(greyscaled_waterfall)s,
                  thresholded_waterfall = %(thresholded_waterfall)s, waterfall_length = %(waterfall_length)s,
                    waterfall_width = %(waterfall_width)s where observation_id = %(observation_id)s;""",
                            {'satnogs_id': satnogs_id, 'satellite_name': satellite_name,
                             'station_name': station_name, 'status': status,
                             'status_code': status_code,
                             'transmitter': transmitter, 'frequency': frequency,
                             'pull_date': datetime.now(),
                             'original_waterfall': original_waterfall,
                             'greyscaled_waterfall': greyscaled_waterfall,
                             'thresholded_waterfall': thresholded_waterfall,
                             'waterfall_length': length,
                             'waterfall_width': width,
                             'observation_id': observation_id})

        except Exception as e:
            print(e)
            return None

    def add_empty_observation(self, satnogs_id):
        self.add_observation(satnogs_id=satnogs_id, satellite_name="tbd",
                             station_name="tbd", status="tbd", status_code=-1, transmitter="tbd", frequency=-1,
                             original_waterfall=b"", greyscaled_waterfall=b"", thresholded_waterfall=b"", length=-1,
                             width=-1)


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
    waterfall_length: int
    waterfall_width: int


if __name__ == "__main__":

    print("\nTesting Observation Interactions\n")

    satnogs_id1 = 7808415
    satnogs_id2 = 7808611

    observation_interactor = ObservationInteractor()
    print("Adding Empty Entry:")
    observation_interactor.add_empty_observation(satnogs_id=satnogs_id2)
    print(observation_interactor.get_observations())

    print("\nAdding Filled Entry:")
    observation_interactor.add_observation(*si.fetch_satnogs(satnogs_id1))
    print(observation_interactor.get_observations())

    print("\nUpdating Empty Entry:")
    observation_id = observation_interactor.get_observation_by_satnogs_id(satnogs_id=satnogs_id2).observation_id
    observation_interactor.update_observation(observation_id, *si.fetch_satnogs(satnogs_id2))
    print(observation_interactor.get_observations())
