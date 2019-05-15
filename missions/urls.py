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

from django.conf.urls import url
import missions.views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$',
        login_required(missions.views.ListMissionView.as_view()), name='missions-list'),
    url(r'^new/$',
        login_required(missions.views.CreateMissionView.as_view()), name='missions-new'),
    url(r'^(?P<pk>\d+)/$',
        login_required(missions.views.EditMissionView.as_view()), name='missions-edit',),
    url(r'^(?P<pk>\d+)/delete/$',
        login_required(missions.views.DeleteMissionView.as_view()), name='missions-delete',),
    url(r'^(?P<mission>\d+)/report/$',
        login_required(missions.views.ReportMissionView.as_view()), name='mission-report',),
    url(r'^(?P<mission>\d+)/attachments/$',
        login_required(missions.views.ReportAttachmentsMissionView.as_view()), name='mission-attachments', ),
    url(r'^(?P<mission>\d+)/stats/$',
        login_required(missions.views.MissionStatsView.as_view()), name='mission-stats',),
    url(r'^(?P<mission_id>\d+)/hosts/$',
        login_required(missions.views.EditMissionHostsView.as_view()), name='mission-hosts'),


    url(r'^(?P<mission>\d+)/tests/$',
        login_required(missions.views.ListMissionTestsView.as_view()), name='mission-tests'),
    url(r'^(?P<mission>\d+)/tests/new/$',
        login_required(missions.views.CreateMissionTestView.as_view()), name='mission-test-new'),
    url(r'^(?P<mission>\d+)/tests/(?P<pk>\d+)/$',
        login_required(missions.views.EditMissionTestView.as_view()), name='mission-test-view'),
    url(r'^(?P<mission>\d+)/tests/(?P<pk>\d+)/edit$',
        login_required(missions.views.EditMissionTestView.as_view()), name='mission-test-edit'),
    url(r'^(?P<mission>\d+)/tests/(?P<pk>\d+)/delete/$',
        login_required(missions.views.DeleteMissionTestView.as_view()), name='mission-test-delete'),
    url(r'^(?P<mission>\d+)/tests/(?P<pk>\d+)/clone/$',
        login_required(missions.views.CloneMissionTestView.as_view()), name='mission-tests-clone'),
    url(r'^(?P<mission>\d+)/tests/reorder/$',
        login_required(missions.views.OrderMissionTestsView.as_view()), name='mission-tests-reorder'),
    url(r'^(?P<mission_id>\d+)/tests/(?P<test_id>\d+)/hosts',
        login_required(missions.views.test_host_handler), name='test-hosts'),

    url(r'^(?P<mission>\d+)/tests/(?P<test_detail>\d+)/data/$',
        login_required(missions.views.ListMissionTestsSupportingDataView.as_view()), name='test-data-list'),
    url(r'^(?P<mission>\d+)/tests/(?P<test_detail>\d+)/data/new/$',
        login_required(missions.views.CreateMissionTestsSupportingDataView.as_view()), name='test-data-new'),
    url(r'^(?P<mission>\d+)/tests/(?P<test_detail>\d+)/data/(?P<pk>\d+)/$',
        login_required(missions.views.EditMissionTestsSupportingDataView.as_view()), name='test-data-edit'),
    url(r'^(?P<mission>\d+)/tests/(?P<test_detail>\d+)/data/(?P<pk>\d+)/delete/$',
        login_required(missions.views.DeleteMissionTestsSupportingDataView.as_view()), name='test-data-delete'),
    url(r'^(?P<mission>\d+)/tests/(?P<test_detail>\d+)/data/reorder/$',
        login_required(missions.views.OrderMissionTestsSupportingDataView.as_view()), name='test-data-reorder'),

]
