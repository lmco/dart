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

"""
Import a mission from a JSON "mission package" exported by the web UI.

Usage:
    python manage.py import_mission <file.json>

The mission is re-created with new ids; supporting-data files are linked only if they
already exist under MEDIA_ROOT (the package's ``files`` array tells you which to copy).
"""

import json
import os

from django.core.management.base import BaseCommand, CommandError

from missions.extras.package import import_mission_from_dict


class Command(BaseCommand):
    help = 'Imports a mission from a DART "mission package" JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('file', help='Path to the exported mission package JSON file.')

    def handle(self, *args, **options):
        package_path = options['file']
        if not os.path.isfile(package_path):
            raise CommandError('No such file: %s' % package_path)

        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            raise CommandError('Unable to read/parse package JSON: %s' % e)

        try:
            mission = import_mission_from_dict(data)
        except ValueError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS(
            'Imported mission "%s" (new id=%s)' % (mission.mission_name, mission.pk)))
        self.stdout.write('  hosts: %s' % mission.host_set.count())
        self.stdout.write('  test cases: %s' % mission.testdetail_set.count())
        self.stdout.write('  supporting data: %s' %
                          sum(t.supportingdata_set.count() for t in mission.testdetail_set.all()))
        self.stdout.write('Supporting-data files must already exist under MEDIA_ROOT '
                          '(see the package "files" array).')