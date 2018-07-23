#!/usr/bin/env bash

JUDGE_ROOT="$(cd $(dirname "$0"); pwd)"

if [ $2 == 'product' ]
    then DJANGO_SETTINGS_MODULE='oj_backend.settings'
elif [ $2 == 'dev' ]
    then DJANGO_SETTINGS_MODULE='oj_backend.settings_dev'
else
    DJANGO_SETTINGS_MODULE='None'
    echo 'Usage: bash judge_receiver.sh -s [product|dev]'
fi

export DJANGO_SETTINGS_MODULE
if [ $DJANGO_SETTINGS_MODULE != 'None' ]
    then celery worker -D --workdir "$JUDGE_ROOT" -A judge_receiver -n judge_receiver.%h -f "$JUDGE_ROOT/celery_judge_receiver.log" --pidfile="$JUDGE_ROOT/celery_judge_receiver.pid" -l warning
#    then celery worker -A judge_receiver -l info
fi

