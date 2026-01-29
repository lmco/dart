<!--
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
-->

# Dart Docker

## Requirements

* admin rights
* git/zip file
* docker

---

## Setup DART docker installation

The following steps will set up DART as a local application running under `localhost:<HOST_PORT>`

> Assumptions: DART root directory is `/DART` (this can be any path you choose, but just make sure to replace this path with yours if it is different)

---

### Clone the repo

1. Open a terminal and navigate to 
    ```
    cd /
    ```
1. Use the git clone command to download the repo

    ```
    $> git clone https://<PATH_TO_THE_REPO>/dart.git
    ```

    > if using a zip just unzip the content in the desired location

---

### Docker

1. Build the image
    ```
    $> docker build --build-arg APPLICATION_PORT=8010 -t dart:latest -f deploy/docker/Dockerfile .
    ```
    > --build-arg : Set build-time variables
    >   - BASE_IMAGE : The base image. Defaults `python`
    >   - BASE_TAG : The image base tag. Defaults `3.11.0-alpine3.16`
    >   - PIP_TRUSTED_HOSTS : pip trusted hosts.Defaults `--trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org`
    >   - APPLICATION_PORT : The app port. Defaults to `8000`
    >   - APPLICATION_DIR : App container directory. Defaults to `/opt/dart`
    >
    >
    > -t : Name and optionally a tag in the `name:tag` format
    > -f : Location of the docker file `deploy/docker/Dockerfile`

1. Run the image
    ```
    $> docker run -d -p <HOST_PORT>:<APPLICATION_PORT>/tcp dart:latest
    ```
    > -d : Run container in background and print container ID
    >
    > -p : Publish a container’s port(s) to the host

---

### Adding users

There are multiple ways of adding users into the app. We'll document one scenario but you are welcome to implement your own. The commands are documented in the django [site](https://docs.djangoproject.com/en/3.2/ref/django-admin/).

1. (Optional) Create a super user (a user who has all permissions). Through this user you will be able to access the admin panels. Type the following command and follow the instructions:
    ```
    $> docker exec -it <CONTAINER_ID> python manage.py createsuperuser

    Username: superuser
    Email address: superuser@dart.com
    Password: 
    Password (again): 
    Superuser created successfully.
    ```

    > Now you should be able to login with the new user
    >
    >To add more users, go to the [user admin panel](http://127.0.0.1:8001/admin/auth/user/) and complete the form to add users.

1. Programmatically creating users:
    Use the `create_user` helper method. For more details look at the [django docs](https://docs.djangoproject.com/en/4.2/topics/auth/default/):
    ```
    $> docker exec -it <CONTAINER_ID> python manage.py shell

    (InteractiveConsole)
    >>> from django.contrib.auth import get_user_model
    >>> user = get_user_model().objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
    >>> user.last_name = "Lennon"
    >>> user.save()
    >>> exit()
    ```