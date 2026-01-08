# Copyright 2026 Lockheed Martin Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

ARG BASE_IMAGE=python
ARG BASE_TAG=3.11.0-alpine3.16
FROM $BASE_IMAGE:$BASE_TAG

LABEL maintainer Lockheed Martin Red Team

ARG PIP_TRUSTED_HOSTS="--trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"

ARG APPLICATION_PORT=8000
ARG APPLICATION_DIR=/opt/dart

ENV REFRESHED_AT=2023-06-01 \
    APPLICATION_PORT=$APPLICATION_PORT

# Add the dart files
ADD ./ $APPLICATION_DIR
WORKDIR $APPLICATION_DIR

RUN pip install -r requirements.txt $PIP_TRUSTED_HOSTS && \
    chown -R 1000:2000 $APPLICATION_DIR && \
    chmod -R 755 $APPLICATION_DIR

VOLUME $APPLICATION_DIR/data/
VOLUME $APPLICATION_DIR/logs/

EXPOSE $APPLICATION_PORT

USER 1000:2000

ENTRYPOINT ["/bin/sh", "deploy/scripts/docker-entrypoint.sh"]

CMD ["sh", "-c", "python ./manage.py runserver 0.0.0.0:${APPLICATION_PORT}"]
