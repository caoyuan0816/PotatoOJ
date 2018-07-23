#!/bin/bash

# This is a install script of PotatoOJ website system.
# It will create a user potatooj to run whole project.
# All files will install in /webapps/PotatoOJ.
# This script need root privilege.

cd "$(dirname "$0")"

CODE_ROOT=`cd .. && pwd`
APP_ROOT="/webapps/PotatoOJ"

## Install dependencies
sudo apt-get update
sudo apt-get install -y postgresql \
                        postgresql-contrib \
                        nginx \
                        python3.4 \
                        build-essential \
                        python-virtualenv \
                        libpq-dev \
                        supervisor

## Create application user potato.
## Group: webapps
sudo groupadd --system webapps
sudo useradd --system --gid webapps --shell /bin/bash --home $APP_ROOT potato
sudo mkdir -p $APP_ROOT
sudo chown potato: $APP_ROOT

### Create database user potato.
sudo su - postgres -c "createuser -d -l potato"
sudo su - potato -c "createdb -O potato -U potato potatooj_db"

## Set up enviroments.
sudo su - potato -c "\
    virtualenv -p /usr/bin/python3 --no-site-packages $APP_ROOT \
    && source $APP_ROOT/bin/activate \
    && pip install django \
                   django-guardian \
                   psycopg2 \
                   gunicorn \
                   setproctitle \
                   djangorestframework \
                   pygments \
                   drfdocs \
                   celery \
                   redis"

## Create log dir
sudo su - potato -c "test -d $APP_ROOT/logs || mkdir -p $APP_ROOT/logs"
sudo su - potato -c "touch $APP_ROOT/logs/gunicorn_supervisor.log"

## Gunicorn
sudo su - potato -c "cp $CODE_ROOT/bin/gunicorn_start.sh $APP_ROOT/bin/ \
    && chmod +x $APP_ROOT/bin/gunicorn_start.sh"

## Supervisor
sudo cp $CODE_ROOT/conf/gunicorn_supervisor.conf /etc/supervisor/conf.d/potatooj.conf

## Nginx
sudo cp $CODE_ROOT/conf/nginx_site_potatooj /etc/nginx/sites-available/potatooj
sudo ln -s /etc/nginx/sites-available/potatooj /etc/nginx/sites-enabled/potatooj
sudo rm /etc/nginx/sites-enabled/default

## Copy static files
sudo su - potato -c "cp -r $CODE_ROOT/static $APP_ROOT/"

## Copy Django files
sudo su - potato -c "cp -r $CODE_ROOT/oj_backend $APP_ROOT/"

### Migrate => move to gunicorn_start.sh
#sudo su - potato -c "source $APP_ROOT/bin/activate \
    #&& python $APP_ROOT/oj_backend/manage.py migrate"

## Run services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
sudo service nginx restart

echo -e "\033[44;37;5m\
=========================\n\
Install finished.\n\
ALL file installed into /webapps/PotatoOJ/, check it!
Don't forget change the password of PostgreSQL user potato and UNIX user potato.\n\

[sudo supervisorctl status] ---> gunicorn status.\n\
[/webapps/PotatoOJ/logs] ---> all log files.\n\
[http://localhost] ---> browse the website.\n\
[source (your virtualenv)/bin/activate]\n\
    ---> activate your own dev enviroment.\n\
[python manage.py runserver --settings=oj_backend.settings_dev 0.0.0.0:8080]\n\
    ---> run dev server.\n\
[python manage.py migrate --database=dev]\n\
    ---> migrate using dev database.\n\
You can change dev-database settings in ROOT_CODE/oj_backend/oj_backend/settings_dev.py \n\
=========================\
\033[0m"




