from __future__ import absolute_import
from celery import shared_task


@shared_task
def judge(run_id, code, language, max_time, max_memory, data_id, is_contest, special_judge=None):
    pass
