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

# Dart Setup

## Requirements

* admin rights
* git/zip file
* python >=3.8
* pip >=20.0

---

## Setup local installation

The following steps will set up DART as a local application running under `localhost:<PORT>`

>Assumptions: DART root directory is /DART (this can be any path you choose, but just make sure to replace this path with yours if it is different).
>
>Might need python3 instead of python depending on the system.

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

### Python virtual environment

1.	From the /DART root directory create a virtual directory by running
    ```
    $> python -m venv .dart-env
    ```
1.	To activate the virtual environment

    **Bash Windows**
    
    ```
    $> source /DART/.dart-env/Scripts/activate
    ```
    
    **Bash Linux**
    
    ```
    $> source /DART/.dart-env/bin/activate
    ```

    **VS Code terminal**

    1.	vscode press ctrl+shft+p
    1.	Search for Python: Select Interpreter
    1.	Select the correct venv (.dart-env)
    1.	Open new terminal
    1.	Verify that the environment is running

        ```
        $> which python
        ```
        >*Should return the location to python inside the .dart-env folder:*
        >**/DART/.dart-env/Scripts/python**

---

### Install dependencies

1.	Run the command

    ```
    $> pip install -r requirements.txt
    ```

    >NOTE: if you run into an issue downloading the packages add the --proxy and/or --trusted-host parameters

---

### Create and seed database

1.	Run database setup script. This script will generate or apply any missing migrations to the database. 

    ```
    $> python manage.py setup-db
    ```

---

### Run the app

1. Run the command

    ```
    $> python manage.py runserver 127.0.0.1:<PORT>
    ```

---

### Stop the app

1. Run the command

    ```
    <CTRL+C>
    ```

---

### Connecting to DART

- Localhost: `127.0.0.1:<PORT>`
- LAN: `<server_ip_address>:8000`

---

### Performing a version upgrade

- With the exception of the following files / locations, replace all DART files (copy and pasting the whole folder should be fine)
  >db.sqlite
  >
  >SUPPORTING\_DATA\_PACKAGE/
  >
  >supporting_data/

- Run the following command

    ```
    $> python manage.py migrate
    ```

- Restart the application
