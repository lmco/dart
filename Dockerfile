FROM alpine:latest
LABEL maintainer Lockheed Martin Red Team

# Copyright 2017 Lockheed Martin Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

###########################################################
# WARNING: Docker support is currently experimental and
# subject to breaking changes at any time. If you deploy
# a docker container, it should be considered ONLY if any
# of the following apply:
#
# 1. You're just giving DART a spin
# 2. Environments where you will NOT need to update DART
# 3. You know what you're doing and are okay with figuring
#    some things out on your own. :)
#
# A note on proxies: a proxy-friendly Dockerfile will be 
# released in the near future. This dockerfile will currently 
# only build when you do not need to specify a proxy to reach
# the internet.
#
# Build this image (on an internet-connected machine) with:
# docker build -t dart:latest .
# 
# Run this image with:
# docker run -d -p8000:8000 dart
###########################################################

ENV REFRESHED_AT 2017-05-25

RUN mkdir -p /var/log/dart

# System preparation
RUN apk update | tee -a /var/log/dart/install.log
RUN apk add python2 | tee -a /var/log/dart/install.log
RUN apk add py-django | tee -a /var/log/dart/install.log
RUN apk add py2-pip | tee -a /var/log/dart/install.log
RUN pip install --upgrade pip | tee -a /var/log/dart/install.log
RUN python --version | tee -a /var/log/dart/install.log
RUN pip --version | tee -a /var/log/dart/install.log
RUN django-admin --version | tee -a /var/log/dart/install.log

# Prep for the compilation of lxml
RUN apk add gcc libc-dev python-dev libxml2-dev libxslt-dev | tee -a /var/log/dart/install.log

# Add the dart files
ADD . /opt/dart/
WORKDIR /opt/dart

# Requirements installation
# 3.6.0 is hard coded for a pre-built Windows wheel,
# here we need to build it so we can grab the latest
RUN echo "Removing version pinning for lxml in requirements.txt" >> /var/log/dart/install.log
RUN sed -i s/lxml==3.6.0/lxml/ requirements.txt
RUN echo "Removed version pinning for lxml in requirements.txt" >> /var/log/dart/install.log
RUN pip install -r requirements.txt | tee -a /var/log/dart/install.log

# Uninstall unneeded build tools and only install required packages
RUN apk del gcc libc-dev python-dev libxml2-dev libxslt-dev | tee -a /var/log/dart/install.log
RUN apk add libxslt | tee -a /var/log/dart/install.log

# Database creation / updates
RUN python manage.py makemigrations | tee -a /var/log/dart/install.log
RUN python manage.py migrate | tee -a /var/log/dart/install.log

# Load all files in missions/fixtures as fixtures
RUN ls missions/fixtures/ | xargs -I FIXTURE python manage.py loaddata FIXTURE | tee -a /var/log/dart/install.log

#TODO: Move db.sqlite3, uploaded data, zips into ./data
VOLUME /opt/dart/data/
VOLUME /opt/dart/missions/migrations/
VOLUME /var/log/dart/

CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000
