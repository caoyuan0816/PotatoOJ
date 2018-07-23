import os
import sys
import ast

import django
from celery import Celery

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT_PATH)
sys.path.append(ROOT_PATH)

django.setup()

from potato.models import Mission, ContestMission, Question

# TODO: read config of judge_receiver celery
# receiver_celery = Celery('receiver')
# receiver_celery.config_from_object(config['Celery_Receiver'])
receiver_celery = Celery('receiver', broker="amqp://potato:potato@test.potatooj.com:5672//judge_receiver")

@receiver_celery.task
def update(run_id, is_contest, status, info=''):
    # TODO: save status into Redis
    # Current: save status into PostgreSQL
    print('Run_id: {} | Is_contest: {} | Status: {} | Info: {}'.format(
        run_id, is_contest, status, info))
    try:
        if not is_contest:
            mission = Mission.objects.get(id=run_id)
            mission.status = status
            mission.judge_info = info
            # Update question statistic datas
            if mission.status > 3:
                # Increasing submit number
                mission.question.submit_num = mission.question.submit_num + 1
                # If accepted
                if mission.status == 4:
                    # Increasing ac number
                    mission.question.ac_num = mission.question.ac_num + 1
            mission.question.save()
            mission.save()
        else:
            contest_misson = ContestMission.objects.get(id=run_id)
            contest_misson.status = status
            contest_misson.judge_info = info
            contest_misson.save()
    except Exception as e:
        # TODO:
        # We need delay and retry in here.
        # Just print Exception is not safe, we can't recieve this task again.
        print(e)
