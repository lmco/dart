# Copyright 2024 Lockheed Martin Corporation
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

"""
DART Database setup script
@description Executes basic initialization of the DART Django project


@notes This can be run more than once, although if you've made changes to the default
       colors, classifications, or BAs, the changes will be reverted (new entries will
       not be affected).
"""

import os
import subprocess
import sys

MANAGER = os.path.join(os.getcwd(), "manage.py")

PYTHON_INTERPRETER = sys.executable

print("\n\nDART First Run Script\nCreated by the Lockheed Martin Red Team")

input("\n\nPress Enter to continue...")

print("\nEnsuring all migrations are made...")
subprocess.call([PYTHON_INTERPRETER, MANAGER, "makemigrations"])

print("\nExecuting migrations...")
subprocess.call([PYTHON_INTERPRETER, MANAGER, "migrate"])

print(
    "\nSeeding the database...\nIf this is not the first time running this script. This step will reset to the default colors, classifications, or BAs from the initial data load. New entries will not be affected."
)
seed_data = input("\nDo you want to seed the database? [y/N]")

if len(seed_data) and seed_data.strip().upper()[0] == "Y":
    print("\nRunning Fixture: common_classifications")
    subprocess.call([PYTHON_INTERPRETER, MANAGER, "loaddata", "common_classifications"])

    print("\nRunning Fixture: common_bas")
    subprocess.call([PYTHON_INTERPRETER, MANAGER, "loaddata", "common_bas"])

add_user = input("\nDo you want add a super user? [y/N]")
while len(add_user) and add_user.strip().upper()[0] == "Y":
    subprocess.call([PYTHON_INTERPRETER, MANAGER, "createsuperuser"])

    add_user = input("\nDo you want add a user? [y/N]")

print("Exiting...")


exit(0)
