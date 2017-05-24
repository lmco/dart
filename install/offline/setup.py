#! /usr/bin/env python
# -*- encoding: utf-8 -*-

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

"""
DART First Run Script
@description Executes basic initialization of the DART Django project
@depends python2.7+
@copyright 2017 Lockheed Martin Corporation
@created 2016-12-22
@modified 2017-02-07
@version 1.1


@notes This can be run more than once, although if you've made changes to the default
       colors, classifications, or BAs, the changes will be reverted (new entries will
       not be affected).
"""

import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALL_DIR = os.path.dirname(SCRIPT_DIR)
DART_ROOT_DIR = os.path.dirname(INSTALL_DIR)
MANAGER = os.path.join(DART_ROOT_DIR, "manage.py")

PYTHON_INTERPRETER = 'python'

print('\n\nDART First Run Script\nCreated by the Lockheed Martin Red Team')

raw_input("\n\nPress Enter to continue...")

print('\nEnsuring all migrations are made...')
subprocess.call([PYTHON_INTERPRETER, MANAGER, "makemigrations"])

print('\nExecuting migrations...')
subprocess.call([PYTHON_INTERPRETER, MANAGER, "migrate"])

print('\nRunning Fixture: common_classifications')
subprocess.call([PYTHON_INTERPRETER, MANAGER, "loaddata", "common_classifications"])

print('\nRunning Fixture: common_bas')
subprocess.call([PYTHON_INTERPRETER, MANAGER, "loaddata", "common_bas"])

raw_input("Press Enter to exit...")
exit(0)
