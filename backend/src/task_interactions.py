from dataclasses import dataclass
from datetime import datetime

import psycopg2 as pg

import postgres_defaults as pod
import observation_interactions as oi


def pprint(L):
    for l in L:
        print(l)


@dataclass
class TaskInteractor:
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

    def add_task(self, observation_id):
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"""insert into tasks (observation_id, status, start_date)
                 values (%(observation_id)s,%(status)s,%(start_date)s);""", {'observation_id': observation_id,
                                                                             'status': "started",
                                                                             'start_date': datetime.now()})

            return True

        except Exception as e:
            print(e)
            return False

    def update_task_by_id(self, task_id, status, finished=False):
        try:
            with self.connection, self.connection.cursor() as cur:
                if not finished:
                    cur.execute(f"""update tasks SET status = %(status)s where task_id = %(task_id)s;""",
                                {'status': status, 'task_id': task_id})
                else:
                    cur.execute(f"""update tasks SET status = %(status)s, completion_date = %(completion_date)s
                     where task_id = %(task_id)s;""", {'status': status, 'task_id': task_id,
                                                       'completion_date': datetime.now()})

            return True

        except Exception as e:
            print(e)
            return False

    def get_tasks(self):
        fetched_tasks = []
        try:
            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from tasks;")

                fetched_tasks = cur.fetchall()

            return [Task(*i) for i in fetched_tasks]

        except Exception as e:
            print(e)
            return fetched_tasks

    def get_task_by_id(self, task_id):
        fetched_task = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from task where task_id = %(task_id)s;",
                            {'task_id': task_id})

                fetched_task = cur.fetchone()

            return Task(*fetched_task) if fetched_task is not None else None

        except Exception as e:
            print(e)
            return fetched_task

    def get_task_by_observation_id(self, observation_id):
        fetched_task = None
        try:

            with self.connection, self.connection.cursor() as cur:
                cur.execute(f"select * from tasks where observation_id = %(observation_id)s;",
                            {'observation_id': observation_id})

                fetched_task = cur.fetchone()

            return Task(*fetched_task) if fetched_task is not None else None

        except Exception as e:
            print(e)
            return fetched_task


@dataclass
class Task:
    task_id: int
    observation_id: int
    status: str
    start: datetime
    completion_date: datetime


if __name__ == "__main__":
    observation_interator = oi.ObservationInteractor()

    task_interactor = TaskInteractor()

    print("\nGetting Task")

    pprint(task_interactor.get_tasks())

    print("\nCreating A Task")

    observation_id = observation_interator.get_observations()[0].observation_id

    task_interactor.add_task(observation_id=observation_id)

    pprint(task_interactor.get_tasks())

    print("\nUpdating A Task")

    task_id = task_interactor.get_tasks()[0].task_id

    task_interactor.update_task_by_id(task_id=task_id, status="Finished", finished=True)

    pprint(task_interactor.get_tasks())

    print("\nCreating A Task and adding an error state")

    observation_id2 = observation_interator.get_observations()[1].observation_id

    task_interactor.add_task(observation_id=observation_id2)

    task_id = task_interactor.get_task_by_observation_id(observation_id=observation_id2).task_id

    task_interactor.update_task_by_id(task_id=task_id, status="Error")

    pprint(task_interactor.get_tasks())
