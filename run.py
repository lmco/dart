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
DART Run Script
@description Starts the DART web app
@depends python2.7+
@copyright 2017 Lockheed Martin Corporation
@created 2016-12-22
@version 1.0
@modified 2016-12-22
"""

import os
import subprocess

DART_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MANAGER = os.path.join(DART_ROOT_DIR, "manage.py")

PYTHON_INTERPRETER = 'python'

print('\n\nDART Run Script\nCreated by the Lockheed Martin Red Team')

print('\n\n***** IMPORTANT *****')
print('Do not close this window until you\'re ready for DART to shutdown.')
print('Run this again when you\'re ready to start again. Your data is saved.')

print('\n\nStarting DART on port 8000, all interfaces...')
print('Navigate to http://<ip_address>:8000 in your browser')

print('\n\nCan\'t login? ')
print('You may need to open a new command window and create a user using the below command:\n')
print(PYTHON_INTERPRETER + " " + MANAGER + " createsuperuser\n")
subprocess.call([PYTHON_INTERPRETER, MANAGER, "runserver", "0.0.0.0:8000"])
