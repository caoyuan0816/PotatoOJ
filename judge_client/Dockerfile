# Judge Client

FROM ubuntu:14.04
MAINTAINER yuan <yuan@yuan25.com>

# Labels
LABEL version="0.2"

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Copy your sources.list
# COPY sources.list /etc/apt/sources.list

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common

RUN DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:webupd8team/java && \
    add-apt-repository -y ppa:git-core/ppa && \
    apt-get update

# Setting building enviroment, including gcc, g++, make, git
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install build-essential git

# Install Python 3
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python python3 python3-pip

# Install Java.
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install oracle-java8-installer && \
    rm -rf /var/cache/oracle-jdk8-installer

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle

# Install build dependencies for lrun
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install libseccomp-dev

# Install lrun
RUN DEBIAN_FRONTEND=noninteractive wget https://github.com/quark-zju/lrun/releases/download/v1.1.4/lrun_1.1.4_amd64.deb -P /var/cache/lrun/ && \
    dpkg -i /var/cache/lrun/lrun_1.1.4_amd64.deb && \
    rm -rf /var/cache/lrun

# Python third libs
RUN DEBIAN_FRONTEND=noninteractive pip3 install celery[redis]

# COPY python scripts
# using docker build -f judge_client/Dockerfile . to build project
COPY judge_client /home/judge/

# Clean
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Change private key authority
RUN chmod 700 /home/judge/conf/git-client-key

WORKDIR /home/judge
CMD bash /home/judge/judge_client.sh
