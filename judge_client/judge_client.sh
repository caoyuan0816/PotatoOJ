#!/usr/bin/env bash

JUDGE_ROOT="$(cd $(dirname "$0"); pwd)"

if [ "$(id -u)" != "0" ]; then
  echo "$0 must be run as root" >&2
  exit 1
fi

if [ -n "$1" ]
    then if [ $1 == '-virtualenv' ]
        then source $JUDGE_ROOT/$2
    fi
fi

export C_FORCE_ROOT="true"

JUDGE_ROOT="$(cd $(dirname "$0"); pwd)"

touch $JUDGE_ROOT/celery_judge.log
celery worker -D --workdir "$JUDGE_ROOT/src" -A judge_task -n judge.%h -f "$JUDGE_ROOT/celery_judge.log" --pidfile="$JUDGE_ROOT/celery_judge.pid" -l warning
tailf $JUDGE_ROOT/celery_judge.log
