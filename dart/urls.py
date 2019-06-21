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

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import missions.views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout, login
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    url(r'^missions/', include('missions.urls')),

    url(r'^$', RedirectView.as_view(url='/missions/', permanent=False)),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/$', RedirectView.as_view(url='/', permanent=False)),
    url(r'^accounts/profile/$', RedirectView.as_view(url='/', permanent=False)),

    url(r'^settings/$',
        login_required(missions.views.UpdateDynamicSettingsView.as_view()), name='update-settings'),
    url(r'^settings/business-areas/$',
        login_required(missions.views.BusinessAreaListView.as_view()), name='list-business-areas'),
    url(r'^settings/update-business-area(?:/(?P<pk>\d+))?/$',
        login_required(missions.views.business_area_handler), name='update-business-area'),
    url(r'^settings/classifications/$',
        login_required(missions.views.ClassificationListView.as_view()), name='list-classifications'),
    url(r'^settings/update-classification(?:/(?P<pk>\d+))?/$',
        login_required(missions.views.classification_handler), name='update-classification'),
    url(r'^settings/colors/$',
        login_required(missions.views.ColorListView.as_view()), name='list-colors'),
    url(r'^settings/update-color(?:/(?P<pk>\d+))?/$',
        login_required(missions.views.color_handler), name='update-color'),
    url(r'^settings/create-account/$',
        missions.views.CreateAccountView.as_view(), name='create-account'),

    url(r'^login-interstitial/$',
        login_required(missions.views.LoginInterstitialView.as_view()), name='login-interstitial'),

    url(r'^about/$',
        login_required(missions.views.AboutTemplateView.as_view()), name='about'),

    url(r'^hosts/(?P<host_id>\d+)/$',
        login_required(missions.views.mission_host_handler), name='host-detail'),

    url(r'^data/(?P<supportingdata>\d+)/$',
        login_required(missions.views.DownloadSupportingDataView.as_view()), name='data-view'),
    url(r'^data/(?P<path>.*)$',
        serve,{'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
]

urlpatterns += staticfiles_urlpatterns()
