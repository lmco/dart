# -*- coding: utf-8 -*-

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

from calendar import timegm
import re
import logging

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.timezone import timedelta, now
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http.response import HttpResponseServerError

logger = logging.getLogger(__name__)


class RequiredInterstitial(object):
    """
    Some organizations may require an acceptable use policy or similar to be displayed upon logon,
    the setting REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL will specify how often the AUP should be displayed
    in hours as a positive integer or 0 to indicate it should be displayed once per application logon.

    Omitting this setting will bypass the interstitial.

    To Use:
    - Add to settings.MIDDLEWARE_CLASSES: 'missions.middleware.RequiredInterstitial'
    - Ensure you specify a value in settings for the key REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL
    """

    def process_request(self, request):
        try:
            display_interval = settings.REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL
        except AttributeError:
            # Setting not defined, so assume we don't want the interstitial to display
            return None
        try:
            if display_interval == 0 \
                    and request.session['last_acknowledged_interstitial']:
                return None
            else:
                max_age = timedelta(hours=display_interval).total_seconds()
                if timegm(now().timetuple()) - request.session['last_acknowledged_interstitial'] < max_age:
                    return None

        except KeyError:
            pass

        path = request.get_full_path()
        if re.match(str(reverse_lazy('login-interstitial')), path) or \
            re.match(str(reverse_lazy('login')), path) or \
            re.match(str(reverse_lazy('logout')), path) or \
            re.match(settings.STATIC_URL + r'.+', path):
            return None

        return redirect('login-interstitial')
