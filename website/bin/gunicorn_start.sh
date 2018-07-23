#!/bin/bash

NAME="PotatoOJ_Django"
ROOT_DIR=/webapps/PotatoOJ
VIRTUALENV_DIR=$ROOT_DIR
DJANGODIR=$ROOT_DIR/oj_backend
SOCKFILE=$ROOT_DIR/run/gunicorn.sock
USER=potato
GROUP=webapps
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=oj_backend.settings
DJANGO_WSGI_MODULE=oj_backend.wsgi

echo "Starting $NAME as `whoami`"

# Activate the virtualenv
source $VIRTUALENV_DIR/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create run dir if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Migrate database
$VIRTUALENV_DIR/bin/python $DJANGODIR/manage.py migrate --database=default

# Start Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec $VIRTUALENV_DIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --bind=unix:$SOCKFILE \
    --log-level=debug \
    --log-file=-

