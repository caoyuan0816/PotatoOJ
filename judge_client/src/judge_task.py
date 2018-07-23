import traceback
from celery import Celery
from judge_client import judge_client
from config import config
from define import JudgeStatus

judge_celery = Celery('judge')
judge_celery.config_from_object(config['Celery_Judge'])

receiver_celery = None


def update_status(*args, **kwargs):
    global receiver_celery
    if not receiver_celery:
        receiver_celery = Celery()
        receiver_celery.config_from_object(config['Celery_Receiver'])

    receiver_celery.send_task('judge_receiver.update', args=args, kwargs=kwargs)


@judge_celery.task(name='potato.tasks.judge')
def judge(run_id, code, language, max_time, max_memory, data_id, is_contest, special_judge=None):
    try:
        client = judge_client(code, int(language), max_time, max_memory, data_id, special_judge)
        for status in client.process():
            print(status)
            if status['status'] in [JudgeStatus.Waiting, JudgeStatus.Compiling, JudgeStatus.Running, JudgeStatus.Judging]:
                status['status'] = status['status'].value
                update_status(run_id, is_contest, **status)
            else:
                # final states, save them into DB
                status['status'] = status['status'].value
                update_status(run_id, is_contest, **status)
    except Exception:
        traceback.print_exc()
        update_status(run_id, is_contest, **{'status': JudgeStatus.SystemError.value, 'info': 'Judge Task fail'})

