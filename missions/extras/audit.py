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

from missions.models import ChangeLog


def log_change(request=None, mission=None, test_detail=None, action='', description='', user=None):
    """
    Records an immutable ChangeLog row for an action on a mission and/or test case.

    Call this explicitly from the create/update/delete/clone views and the import
    command (signals don't have access to the requesting user). All protected endpoints
    have a real ``request.user``; :param user: overrides request-derived user.
    """
    if user is None and request is not None:
        user = request.user if request.user.is_authenticated else None

    ChangeLog.objects.create(
        mission=mission,
        test_detail=test_detail,
        user=user,
        action=action,
        description=description,
    )