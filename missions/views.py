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

import json
import logging
import mimetypes
import time
from calendar import timegm
from http.client import BAD_REQUEST, NOT_ACCEPTABLE
from itertools import chain

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.signing import Signer
from django.urls import reverse, reverse_lazy, resolve
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.utils.html import conditional_escape
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View, DeleteView

from .extras.audit import log_change
from .extras.helpers.analytics import MissionAnalytics
from .extras.helpers.sorters import TestSortingHelper
from .extras.package import export_mission_json
from .extras.utils import ReturnStatus, generate_report_or_attachments
from .models import Mission, TestDetail, SupportingData, DARTDynamicSettings, Host, BusinessArea, \
    ClassificationLegend, Color, ChangeLog

logger = logging.getLogger(__name__)


def _render_version_conflict(view, form, version_field='version'):
    """
    Optimistic-lock check for editable forms.

    If the stored version of ``view``'s object is newer than the version the submitted
    form was rendered with, someone else saved in the meantime. Return a re-rendered
    response bound to the FRESH instance (so the user sees current values and the latest
    version) with a warning; otherwise return None so the caller proceeds to save.
    """
    current = view.get_object()
    try:
        submitted = int(view.request.POST.get(version_field, 0) or 0)
    except (TypeError, ValueError):
        submitted = 0

    if current.version > submitted:
        logger.info(
            'Version conflict on %s pk=%s (stored=%s submitted=%s) by user=%s',
            type(current).__name__, current.pk, current.version, submitted,
            view.request.user.username if view.request.user.is_authenticated else '<anon>',
        )
        messages.warning(
            view.request,
            'This record was modified by someone else while you were editing. '
            'Your changes were NOT saved. Review the current values and re-submit.',
        )
        # Rebind to the fresh instance so the page shows the latest data + version.
        form = view.get_form_class()(instance=current)
        return view.render_to_response(view.get_context_data(form=form))
    return None


def _bump_version(instance):
    """Increment the optimistic-lock version without re-triggering save()."""
    type(instance).objects.filter(pk=instance.pk).update(version=F('version') + 1)


class UpdateDynamicSettingsView(UpdateView):
    success_url = reverse_lazy('missions-list')
    template_name = 'update_dynamic_settings.html'

    fields = [
        'system_classification',
        'host_output_format'
    ]

    def get_object(self):
        return DARTDynamicSettings.objects.get_as_object()

    def post(self, request, *args, **kwargs):

        # Delete cached data for the legends
        legend_top_key = make_template_fragment_key('legend_partial_top')
        cache.delete(legend_top_key)
        legend_bottom_key = make_template_fragment_key('legend_partial_bottom')
        cache.delete(legend_bottom_key)

        # Drop the memoized host output format string so hosts render with the new format
        Host.invalidate_host_output_format_cache()

        return super(UpdateDynamicSettingsView, self).post(request, *args, **kwargs)


class ListMissionView(ListView):
    model = Mission
    template_name = 'mission_list.html'

    def get_context_data(self, **kwargs):
        logger.debug('GET: ListMissionView')
        context = super(ListMissionView, self).get_context_data(**kwargs)
        missions = Mission.objects.all().order_by('id')
        paginator = Paginator(missions, 10)
        page = self.request.GET.get('page')
        try:
            show_missions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_missions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_missions = paginator.page(paginator.num_pages)
        context['missions'] = show_missions
        return context


class CreateMissionView(CreateView):
    model = Mission
    template_name = 'edit_mission.html'
    fields = [
        'mission_name',
        'mission_number',
        'test_case_identifier',
        'business_area',
        'introduction',
        'scope',
        'objectives',
        'executive_summary',
        'technical_assessment_overview',
        'conclusion',
        'attack_phase_include_flag',
        'attack_type_include_flag',
        'assumptions_include_flag',
        'test_description_include_flag',
        'findings_include_flag',
        'mitigation_include_flag',
        'tools_used_include_flag',
        'command_syntax_include_flag',
        'targets_include_flag',
        'sources_include_flag',
        'attack_time_date_include_flag',
        'attack_side_effects_include_flag',
        'test_result_observation_include_flag',
        'supporting_data_include_flag',
        'customer_notes_include_flag',
    ]

    def form_valid(self, form):
        self.object = form.save()
        log_change(request=self.request, mission=self.object, action='created')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        logger.debug('Created mission {mission_id}'.format(mission_id=self.object.id))
        return reverse('missions-list')

    def get_context_data(self, **kwargs):
        logger.debug('GET: CreateMissionView')
        context = super(CreateMissionView, self).get_context_data(**kwargs)
        context['action'] = reverse('missions-new')
        return context


class EditMissionView(UpdateView):
    model = Mission
    template_name = 'edit_mission.html'
    fields = [
        'mission_name',
        'mission_number',
        'test_case_identifier',
        'business_area',
        'introduction',
        'scope',
        'objectives',
        'executive_summary',
        'technical_assessment_overview',
        'conclusion',
        'attack_phase_include_flag',
        'attack_type_include_flag',
        'assumptions_include_flag',
        'test_description_include_flag',
        'findings_include_flag',
        'mitigation_include_flag',
        'tools_used_include_flag',
        'command_syntax_include_flag',
        'targets_include_flag',
        'sources_include_flag',
        'attack_time_date_include_flag',
        'attack_side_effects_include_flag',
        'test_result_observation_include_flag',
        'supporting_data_include_flag',
        'customer_notes_include_flag',
    ]

    def get_success_url(self):
        logger.debug('POST: EditMissionView (Saved {mission_id})'.format(mission_id=self.object.id))
        return reverse('missions-list')

    def form_valid(self, form):
        conflict = _render_version_conflict(self, form)
        if conflict:
            return conflict
        self.object = form.save()
        _bump_version(self.object)
        log_change(request=self.request, mission=self.object, action='updated')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        logger.debug('GET: EditMissionView (Edit {mission_id})'.format(mission_id=self.get_object().id))
        context = super(EditMissionView, self).get_context_data(**kwargs)
        context['action'] = reverse('missions-edit', kwargs={'pk': self.get_object().id})
        context['mission_changelogs'] = ChangeLog.objects.filter(
            mission=self.get_object()
        ).select_related('user').order_by('-timestamp')[:25]
        return context


class DeleteMissionView(DeleteView):
    model = Mission
    template_name = 'delete_mission.html'

    def get_context_data(self, **kwargs):
        logger.debug('GET: DeleteMissionView (Confirm delete {mission_id})'
                     .format(mission_id=self.object.id))
        return super(DeleteMissionView, self).get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        # Log before actually deleting so we still have the pk/name
        mission = self.get_object()
        log_change(request=request, mission=mission, action='deleted',
                   description='Deleted mission "%s"' % mission.mission_name)
        return super(DeleteMissionView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        logger.debug('POST: DeleteMisisonView (Deleted {mission_id})'.format(mission_id=self.object.id))
        return reverse('missions-list')


class ReportMissionView(View):

    def get(self, request, *args, **kwargs):

        mission_id = kwargs.get('mission')

        logger.debug('GET: ReportMissionView ({mission_id})'.format(mission_id=mission_id))

        io_stream, name = generate_report_or_attachments(mission_id, zip_attachments=False)
        docx_name = name + "_" + str(mission_id)

        response = HttpResponse(
            io_stream.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={}_mission_report.docx'.format(docx_name)
        return response


class ReportAttachmentsMissionView(View):

    def get(self, request, *args, **kwargs):

        mission_id = kwargs.get('mission')

        logger.debug('GET: ReportAttachmentsMissionView ({mission_id})'.format(mission_id=mission_id))

        io_stream, name = generate_report_or_attachments(mission_id, zip_attachments=True)
        zip_name = name + "_" + str(mission_id)

        response = HttpResponse(io_stream.getvalue(), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={}_supporting_data.zip'.format(zip_name)
        return response


class ExportMissionView(View):
    """Downloads the mission structure as a portable JSON "package"."""

    def get(self, request, *args, **kwargs):
        mission_id = kwargs.get('mission')
        mission = Mission.objects.get(id=mission_id)

        logger.debug('GET: ExportMissionView ({mission_id})'.format(mission_id=mission_id))

        payload = export_mission_json(mission)
        safe_name = mission.mission_name.strip().replace('/', '-')
        response = HttpResponse(
            payload,
            content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename={}_{}_mission_export.json'.format(
            safe_name, mission_id)
        return response


class MissionStatsView(TemplateView):
    template_name = 'mission_stats_partial.html'

    def get_context_data(self, **kwargs):
        context = super(MissionStatsView, self).get_context_data(**kwargs)

        context['analytics'] = MissionAnalytics(self.kwargs['mission'])

        return context


class ListMissionTestsView(ListView):
    model = TestDetail
    template_name = 'mission_list_tests.html'

    def get_queryset(self):
        return TestSortingHelper.get_ordered_testdetails(self.kwargs['mission'])

    def get_context_data(self, **kwargs):
        context = super(ListMissionTestsView, self).get_context_data(**kwargs)
        tests = self.get_queryset()

        context['tests'] = tests
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])

        context['server_timestamp'] = Signer().sign(time.time())
        return context


class OrderMissionTestsView(View):
    def post(self, request, *args, **kwargs):
        """ Accepts a posted JSON string to specify new test case sort order """
        mission_id = self.kwargs['mission']
        new_order = []

        # Ensure the received value is just ints
        try:
            data = json.loads(request.body)
            for i in data['order']:
                new_order.append(int(i))
        except ValueError:
            logger.exception('POST: OrderMissionTestsView received non-ints')
            raise  # Maybe do something else here one day

        # A user with a stale Tests list may override a newer sort order inadvertently
        # TODO: Add confirmation check if data['server_timestamp'] is older than the last update of the db field

        try:
            tests = TestDetail.objects.filter(mission=self.kwargs['mission'])
        except TestDetail.DoesNotExist:
            tests = ()

        # Update mission record with the new order
        mission = Mission.objects.get(pk=mission_id)
        current_order = json.loads(mission.testdetail_sort_order)

        # Check to see if new test cases have been created since the page was rendered to this user
        # if so, just append the missing test cases to the tail end so they don't disappear
        if len(new_order) < len(current_order):
            for i in current_order:
                if i not in new_order:
                    new_order.append(i)

        mission.testdetail_sort_order = json.dumps(new_order)
        mission.save(update_fields=['testdetail_sort_order'])
        rs = ReturnStatus(message="Order Updated")
        return HttpResponse(rs.to_json())


class CloneMissionTestView(View):
    def get(self, request, *args, **kwargs):
        """ Makes a clone within the current mission of a specified test case """

        # Verify the test case passed is an int and within the path's mission
        id_to_clone = int(self.kwargs['pk'])
        passed_mission_id = int(self.kwargs['mission'])

        try:
            test_case = TestDetail.objects.get(pk=id_to_clone)
        except TestDetail.DoesNotExist:
            return HttpResponse("Test case not found.", status=404)

        if test_case.mission.id != passed_mission_id:
            return HttpResponse("Test case not linked to specified mission.", status=400)

        test_case.pk = None
        test_case.test_case_status = 'NEW'
        test_case.save()

        log_change(request=request, test_detail=test_case,
                   mission=test_case.mission, action='cloned',
                   description='Cloned from test case #%s' % id_to_clone)

        return HttpResponse(reverse_lazy('mission-test-edit',
                            kwargs={'mission': test_case.mission.id, 'pk': test_case.pk}))


class CloneMissionView(View):
    """Deep-copies a whole mission: hosts, test cases, and supporting-data records."""

    def get(self, request, *args, **kwargs):
        source_mission = Mission.objects.get(pk=self.kwargs['pk'])

        # ---- Mission (new pk/version; copy every other scalar) ----
        new_mission = Mission.objects.create(
            **{f.name: getattr(source_mission, f.name)
               for f in Mission._meta.fields if f.name not in ('id', 'version')}
        )
        new_mission.mission_name = source_mission.mission_name + ' (Clone)'
        new_mission.testdetail_sort_order = '[]'
        new_mission.save(update_fields=['mission_name', 'testdetail_sort_order'])

        # ---- Hosts ----
        host_map = {}  # old host id -> new host id
        for host in source_mission.host_set.all():
            new_host = Host.objects.create(
                **{f.name: getattr(host, f.name)
                   for f in Host._meta.fields if f.name not in ('id', 'mission')}
            )
            new_host.mission = new_mission
            new_host.save()
            host_map[host.id] = new_host.id

        # ---- Tests ----
        test_map = {}  # old test id -> new test id
        source_order = json.loads(source_mission.testdetail_sort_order or '[]')
        for old_test in TestDetail.objects.filter(mission=source_mission):
            test_scalars = {f.name: getattr(old_test, f.name)
                            for f in TestDetail._meta.fields
                            if f.name not in ('id', 'version', 'mission',
                                              'source_hosts', 'target_hosts')}
            test_scalars['test_case_status'] = 'NEW'
            test_scalars['supporting_data_sort_order'] = '[]'
            new_test = TestDetail.objects.create(mission=new_mission, **test_scalars)

            # M2M after both hosts + this test exist
            new_test.source_hosts.set(host_map[h.id] for h in old_test.source_hosts.all() if h.id in host_map)
            new_test.target_hosts.set(host_map[h.id] for h in old_test.target_hosts.all() if h.id in host_map)

            # Supporting data (files already on disk under MEDIA_ROOT; link new records)
            for sd in old_test.supportingdata_set.all():
                SupportingData.objects.create(
                    test_detail=new_test,
                    caption=sd.caption,
                    include_flag=sd.include_flag,
                    test_file=sd.test_file.name,
                )

            test_map[old_test.id] = new_test.id

        # ---- Rebuild mission test order (old -> new where present) ----
        new_order = [test_map[i] for i in source_order if i in test_map]
        # Include any tests not present in the source order (defensive)
        new_order += [v for k, v in test_map.items() if v not in new_order]
        new_mission.testdetail_sort_order = json.dumps(new_order)
        new_mission.save(update_fields=['testdetail_sort_order'])

        log_change(request=request, mission=new_mission, action='cloned',
                   description='Cloned from mission "%s" (#%s)' % (
                       source_mission.mission_name, source_mission.pk))

        return redirect('missions-edit', pk=new_mission.pk)


class DeleteMissionTestView(DeleteView):
    model = TestDetail
    template_name = 'delete_test.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteMissionTestView, self).get_context_data(**kwargs)
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])
        context['test_id'] = self.kwargs['pk']
        return context

    def delete(self, request, *args, **kwargs):
        test = self.get_object()
        log_change(request=request, test_detail=test, mission=test.mission, action='deleted',
                   description='Deleted test case "%s"' % test.test_objective)
        return super(DeleteMissionTestView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mission-tests', kwargs={'mission': self.kwargs['mission']})


class CreateMissionTestView(CreateView):
    model = TestDetail
    template_name = 'edit_mission_test.html'
    fields = [
        'test_case_include_flag',
        'test_case_status',
        'point_of_contact',
        'enclave',
        'test_objective',
        'attack_phase',
        'attack_phase_include_flag',
        'attack_type',
        'attack_type_include_flag',
        'assumptions',
        'assumptions_include_flag',
        're_eval_test_case_number',
        'test_description',
        'test_description_include_flag',
        'sources_include_flag',
        'targets_include_flag',
        'tools_used',
        'tools_used_include_flag',
        'command_syntax',
        'command_syntax_include_flag',
        'attack_time_date',
        'attack_time_date_include_flag',
        'test_result_observation',
        'test_result_observation_include_flag',
        'execution_status',
        'attack_side_effects',
        'attack_side_effects_include_flag',
        'findings',
        'findings_include_flag',
        'mitigation',
        'mitigation_include_flag',
    ]

    def get_success_url(self):
        return reverse('mission-tests', kwargs={'mission': self.kwargs['mission']})

    def get_context_data(self, **kwargs):
        context = super(CreateMissionTestView, self).get_context_data(**kwargs)
        context['action'] = reverse('mission-test-new', kwargs={'mission': self.kwargs['mission']})
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])
        context['display_navbar_save_button'] = True
        return context

    def form_valid(self, form):
        form.instance.mission_id = self.kwargs['mission']
        self.object = form.save()
        log_change(request=self.request, test_detail=self.object,
                   mission=self.object.mission, action='created')
        return HttpResponseRedirect(self.get_success_url())


class EditMissionTestView(UpdateView):
    model = TestDetail
    template_name = 'edit_mission_test.html'
    fields = [
        'test_case_include_flag',
        'test_case_status',
        'point_of_contact',
        'enclave',
        'test_objective',
        'attack_phase',
        'attack_phase_include_flag',
        'attack_type',
        'attack_type_include_flag',
        'assumptions',
        'assumptions_include_flag',
        're_eval_test_case_number',
        'test_description',
        'test_description_include_flag',
        'sources_include_flag',
        'targets_include_flag',
        'tools_used',
        'tools_used_include_flag',
        'command_syntax',
        'command_syntax_include_flag',
        'attack_time_date',
        'attack_time_date_include_flag',
        'test_result_observation',
        'test_result_observation_include_flag',
        'execution_status',
        'attack_side_effects',
        'attack_side_effects_include_flag',
        'findings',
        'findings_include_flag',
        'mitigation',
        'mitigation_include_flag',
    ]

    def get_success_url(self):
        return reverse('mission-tests', kwargs={'mission': self.kwargs['mission']})

    def form_valid(self, form):
        conflict = _render_version_conflict(self, form)
        if conflict:
            return conflict
        self.object = form.save()
        _bump_version(self.object)
        log_change(request=self.request, test_detail=self.object,
                   mission=self.object.mission, action='updated')
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(EditMissionTestView, self).get_context_data(**kwargs)
        context['action'] = reverse('mission-test-edit', kwargs={'pk': self.get_object().id,
                                                                 'mission': self.kwargs['mission']})
        mission_model = Mission.objects.get(id=self.kwargs['mission'])
        context['this_mission'] = mission_model

        context['test_changelogs'] = ChangeLog.objects.filter(
            test_detail=self.get_object()
        ).select_related('user').order_by('-timestamp')[:25]

        context['display_navbar_save_button'] = True
        context['is_read_only'] = resolve(self.request.path_info).url_name == 'mission-test-view'
        if self.request.GET.get('scrollPos'):
            try:
                context['scrollPos'] = int(self.request.GET.get('scrollPos'))
            except ValueError:
                logger.exception('URL Parameter scrollPos invalid (not an int); setting to None. '
                                 '(Logged in user: {user})'.format(user=self.request.user.username or "**Anonymous**"))
                context['scrollPos'] = None
        return context


class ListMissionTestsSupportingDataView(ListView):
    model = TestDetail
    template_name = 'test_supporting_data_list.html'

    def get_queryset(self):
        return TestSortingHelper.get_ordered_supporting_data(self.kwargs['test_detail'])

    def get_context_data(self, **kwargs):
        context = super(ListMissionTestsSupportingDataView, self).get_context_data(**kwargs)
        testdata = self.get_queryset()
        paginator = Paginator(testdata, 10)
        page = self.request.GET.get('page')
        try:
            show_data = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_data = paginator.page(paginator.num_pages)
        context['show_data'] = show_data
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])
        context['this_test'] = TestDetail.objects.get(id=self.kwargs['test_detail'])
        return context


class CreateMissionTestsSupportingDataView(CreateView):
    model = SupportingData
    template_name = 'edit_test_data.html'
    fields = ['caption', 'test_file', 'include_flag']

    def get_success_url(self):
        return reverse('test-data-list', kwargs={'mission': self.kwargs['mission'], 'test_detail': self.kwargs['test_detail']})

    def get_context_data(self, **kwargs):
        context = super(CreateMissionTestsSupportingDataView, self).get_context_data(**kwargs)
        context['action'] = reverse('test-data-new', kwargs={'mission': self.kwargs['mission'], 'test_detail': self.kwargs['test_detail']})
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])
        context['this_test'] = TestDetail.objects.get(id=self.kwargs['test_detail'])
        return context

    def form_valid(self, form):
        form.instance.test_detail_id = self.kwargs['test_detail']
        return super(CreateMissionTestsSupportingDataView, self).form_valid(form)


class EditMissionTestsSupportingDataView(UpdateView):
    model = SupportingData
    template_name = 'edit_test_data.html'
    fields = ['caption', 'test_file', 'include_flag']

    def get_success_url(self):
        return reverse('test-data-list', kwargs={'mission': self.kwargs['mission'],
                                                 'test_detail': self.kwargs['test_detail']})

    def get_context_data(self, **kwargs):
        context = super(EditMissionTestsSupportingDataView, self).get_context_data(**kwargs)
        context['action'] = reverse('test-data-edit', kwargs={'pk': self.get_object().id,
                                                              'mission': self.kwargs['mission'],
                                                              'test_detail': self.kwargs['test_detail']})
        context['this_mission'] = Mission.objects.get(id=self.kwargs['mission'])
        context['this_test'] = TestDetail.objects.get(id=self.kwargs['test_detail'])
        return context


class DeleteMissionTestsSupportingDataView(DeleteView):
    model = SupportingData
    template_name = 'delete_test_data.html'

    def get_context_data(self, **kwargs):
        context = super(DeleteMissionTestsSupportingDataView, self).get_context_data(**kwargs)
        context['mission_id'] = self.kwargs['mission']
        context['test_id'] = self.kwargs['test_detail']
        return context

    def get_success_url(self):
        return reverse('test-data-list', kwargs={'mission': self.kwargs['mission'], 'test_detail': self.kwargs['test_detail']})


class OrderMissionTestsSupportingDataView(View):
    def post(self, request, *args, **kwargs):
        """ Accepts a posted JSON string to specify new test case sort order """
        mission_id = self.kwargs['mission']
        test_detail_id = self.kwargs['test_detail']
        new_order = []

        # Ensure the received value is just ints
        try:
            data = json.loads(request.body)
            for i in data['order']:
                new_order.append(int(i))
        except ValueError:
            logger.exception('POST: OrderMissionTestsSupportingDataView received non-ints')
            raise

        # Update testdetail record with the new order
        testdetail = TestDetail.objects.get(pk=test_detail_id)
        current_order = json.loads(testdetail.supporting_data_sort_order)

        # Check to see if new supporting data has been have been created since the page was rendered to this user
        # if so, just append the missing data to the tail end so they don't disappear
        if len(new_order) < len(current_order):
            for i in current_order:
                if i not in new_order:
                    new_order.append(i)

        testdetail.supporting_data_sort_order = json.dumps(new_order)
        testdetail.save(update_fields=['supporting_data_sort_order'])
        rs = ReturnStatus(message="Supporting Data Order Updated")
        return HttpResponse(rs.to_json())


class DownloadSupportingDataView(View):
    model = SupportingData

    def get(self, request, *args, **kwargs):
        supporting_data_object = SupportingData.objects.get(id=self.kwargs['supportingdata'])

        # Backwards compatibility shim for #106 fix
        if str(supporting_data_object.test_file.name).startswith('supporting_data/'):
            supporting_data_object.test_file.name = supporting_data_object.test_file.name[16:]
            supporting_data_object.save()

        filename = supporting_data_object.filename()
        response = HttpResponse(
            supporting_data_object.test_file.file,
            content_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class LoginInterstitialView(TemplateView):
    template_name = 'login_interstitial.html'

    def post(self, request):
        request.session['last_acknowledged_interstitial'] = timegm(now().timetuple())
        request.session.save()
        logger.info('User ({user}) acknowledged and accepted the login interstitial'.format(
            user=request.user.username
        ))
        return redirect('missions-list')


class CreateAccountView(TemplateView):
    template_name = 'create_account.html'

    @staticmethod
    def any_accounts_configured():
        '''
        Determines if there are any accounts currently configured.
        :return: Boolean
        '''
        User = get_user_model()
        return User.objects.all().exists()

    def get_context_data(self, **kwargs):
        context = super(CreateAccountView, self).get_context_data(**kwargs)
        context['any_accounts_configured'] = self.any_accounts_configured()
        return context

    def post(self, request):

        # This view can only process posts if there are *no* configured accounts whatsoever
        if self.any_accounts_configured():
            return redirect('logout')
        else:
            User = get_user_model()

            username = request.POST['username']
            password = request.POST['password']

            User.objects.create_superuser(username, username + '@dart.local', password)

            return redirect('login')


class EditMissionHostsView(TemplateView):
    template_name = 'edit_mission_hosts.html'

    def get_context_data(self, **kwargs):
        context = super(EditMissionHostsView, self).get_context_data(**kwargs)
        context['mission'] = Mission.objects.prefetch_related('host_set').get(pk=int(kwargs.get('mission_id')))
        return context


@require_http_methods(["GET", "POST", "DELETE"])
def mission_host_handler(request, host_id):

    if request.method == "GET":
        try:
            host = Host.objects.get(pk=int(host_id))
            data = {
                'id': host.id,
                'is_no_hit': host.is_no_hit,
                'mission': host.mission.pk,
                'host_name': host.host_name, 
                'display': conditional_escape(host),
                'ip_address': conditional_escape(host.ip_address),
            }

            status = ReturnStatus(
                message='OK',
                data=data,
            )
            return JsonResponse(status.to_dict())

        except Host.DoesNotExist:
            status = ReturnStatus(
                success=False,
                message='Unable to locate mission.',
            )
            return JsonResponse(status.to_dict())

    if request.method == "POST":
        try:
            if len(request.body) > 0:
                data = json.loads(request.body)
                logger.debug('Host update POST data successfully read as json.')

                try:
                    host = Host.objects.get(pk=int(host_id))
                    logger.debug('Host update POST pk value is valid.')
                except Host.DoesNotExist:
                    logger.debug('Host update POST pk value does not correspond to a host in the host_set.')
                    logger.debug('Host update POST is creating a new host.')
                    host = Host()

                if host.pk is None:
                    # Hosts shouldn't be jumping between missions, so only allow mission assignment upon creation
                    if 'mission_id' in list(data.keys()):
                        logger.debug('Host update POST contains a mission pk value.')
                        try:
                            host.mission = Mission.objects.get(pk=int(data['mission_id']))
                        except Mission.DoesNotExist:
                            error_message = 'Unable to find mission.'
                            logger.debug(error_message)
                            return JsonResponse(ReturnStatus(False, error_message).to_dict())
                    else:
                        error_message = 'Host requires an associated mission (not provided).'
                        logger.debug(error_message)
                        return JsonResponse(ReturnStatus(False, error_message).to_dict())

                try:
                    was_new = host.pk is None
                    host.host_name = data['host_name']
                    host.ip_address = data['ip_address']
                    host.is_no_hit = data['is_no_hit']
                    host.save()
                    # Audit the host add/update against its mission
                    action = 'host_added' if was_new else 'host_updated'
                    log_change(request=request, mission=host.mission, action=action,
                               description='Host %s (%s)' % (data.get('host_name', ''), data.get('ip_address', '')))
                    logger.debug('Host update POST saved host.')
                    return JsonResponse(ReturnStatus(message='OK', data={'pk': host.pk}).to_dict())
                except KeyError:
                    error_message = 'Required field(s) missing from host update / creation.'
                    logger.debug(error_message)
                    return JsonResponse(ReturnStatus(success=False, message=error_message).to_dict())

        except ValueError as e:
            # Probably a json decode error or a non-int value for a pk
            error_message = 'Unable to process request.'
            logger.exception(exc_info=e)
            return JsonResponse(ReturnStatus(success=False, message=error_message).to_dict())

    if request.method == "DELETE":
        try:
            host = Host.objects.get(pk=int(host_id))

            target_set = host.target_set.all()
            source_set = host.source_set.all()

            combined_set = list(chain(target_set, source_set))

            if len(combined_set) > 0:
                test_ids = set()
                for test in combined_set:
                    test_ids.add(str(test.pk))
                error_message = "Host {host} is currently listed as a source or target on one or more test cases. " \
                                "Please remove the host from the following test cases: {ids}".format(
                                    host=host.pk,
                                    ids=','.join(test_ids),
                                )
                logger.debug(error_message)
                status = ReturnStatus(False, error_message)
                return JsonResponse(status.to_dict(), status=NOT_ACCEPTABLE)
            else:
                log_change(request=request, mission=host.mission, action='host_deleted',
                           description='Host %s (%s)' % (host.host_name, host.ip_address))
                host.delete()
                return JsonResponse(ReturnStatus(message='OK', data={"pk": host_id}).to_dict())
        except Host.DoesNotExist:
            error_message = 'Tried to delete {}, but there is no such host.'.format(
                host_id
            )
            logger.debug(error_message)
            return JsonResponse(ReturnStatus(False, error_message).to_dict(), status=BAD_REQUEST)

        except ValueError:
            error_message = 'Tried to delete {}, but there was a problem.'.format(
                host_id
            )
            logger.debug(error_message)
            return JsonResponse(ReturnStatus(False, error_message).to_dict())


@require_http_methods(["GET", "POST", "DELETE"])
def test_host_handler(request, mission_id, test_id):

    if request.method == 'GET':

        try:
            testcase = TestDetail.objects.prefetch_related('target_hosts').prefetch_related('source_hosts').get(pk=test_id)

        except TestDetail.DoesNotExist:
            error_message = 'test_host_handler GET Test does not exist'
            logger.debug(error_message)
            return JsonResponse(ReturnStatus(False, error_message).to_dict())

        data = []

        for host in testcase.target_hosts.all():
            data.append(
                {
                    'id': host.id,
                    'is_no_hit': host.is_no_hit,
                    'mission': host.mission.pk,
                    'host_name': conditional_escape(host.host_name),
                    'role': 'target',
                    'display': conditional_escape(host)
                }
            )

        for host in testcase.source_hosts.all():
            data.append(
                {
                    'id': host.id,
                    'is_no_hit': host.is_no_hit,
                    'mission': host.mission.pk,
                    'host_name': conditional_escape(host.host_name),
                    'role': 'source',
                    'display': conditional_escape(host),
                }
            )

        unassigned_hosts = Host.objects.filter(mission=testcase.mission)

        for host in unassigned_hosts.all():
            data.append(
                {
                    'id': host.id,
                    'is_no_hit': host.is_no_hit,
                    'mission': host.mission.pk,
                    'host_name': conditional_escape(host.host_name),
                    'role': '',
                    'display': conditional_escape(host),
                }
            )

        status = ReturnStatus()
        status.data = data

        return JsonResponse(status.to_dict())

    if request.method == 'POST':
        try:
            if len(request.body) > 0:
                data = json.loads(request.body)
                logger.debug('test_host_handler POST data successfully read as json.')

                try:
                    host_id = data['host_id']
                    role = data['role']
                except KeyError:
                    error_message = 'Missing required key'
                    logger.debug('test_host_handler POST ' + error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                try:
                    host = Host.objects.get(pk=host_id)
                except Host.DoesNotExist:
                    error_message = 'No such host'
                    logger.debug('test_host_handler POST ' + error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                try:
                    testcase = TestDetail.objects.get(pk=test_id)
                except TestDetail.DoesNotExist:
                    error_message = 'No such test case'
                    logger.debug('test_host_handler POST ' + error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                if host.mission != testcase.mission:
                    error_message = 'Host not in mission scope'
                    logger.debug('test_host_handler POST ' + error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                if host.is_no_hit:
                    error_message = 'Host is on the no hit list'
                    logger.debug('test_host_handler POST ' + error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                if role == 'target':
                    testcase.target_hosts.add(host)
                elif role == 'source':
                    testcase.source_hosts.add(host)

                logger.debug('test_host_handler POST added host {} to testcase {}'.format(
                    host.pk,
                    testcase.pk,
                ))

                return JsonResponse(ReturnStatus(True, "OK").to_dict())

        except ValueError:
            logger.debug('test_host_handler POST encountered an error decoding the JSON input')
            return JsonResponse(ReturnStatus(False, 'Invalid json received').to_dict())

    if request.method == 'DELETE':
        try:
            if len(request.body) > 0:
                data = json.loads(request.body)
                logger.debug('test_host_handler DELETE data successfully read as json.')

                try:
                    host = Host.objects.get(pk=int(data['host_id']))
                    logger.debug('test_host_handler DELETE host pk value exists.')
                except Host.DoesNotExist:
                    error_message = 'test_host_handler DELETE host pk value does not exist.'.format(
                        data['host_id']
                    )
                    logger.debug(error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                try:
                    testcase = TestDetail.objects.get(pk=test_id)
                    logger.debug('test_host_handler DELETE test case pk value exists.')
                except Host.DoesNotExist:
                    error_message = 'test_host_handler DELETE test case pk value does not exist.'.format(
                        data['host_id']
                    )
                    logger.debug(error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

                if data['role'] == 'target':
                    logger.debug('test_host_handler deleting host from targets')
                    testcase.target_hosts.remove(host)
                    logger.debug('test_host_handler deleting host from targets')
                    return JsonResponse(ReturnStatus(True, 'OK').to_dict())

                elif data['role'] == 'source':
                    logger.debug('test_host_handler deleting host from sources')
                    testcase.source_hosts.remove(host)
                    logger.debug('test_host_handler deleting host from sources')
                    return JsonResponse(ReturnStatus(True, 'OK').to_dict())

                else:
                    error_message = 'test_host_handler DELETE role unknown.'
                    logger.debug(error_message)
                    return JsonResponse(ReturnStatus(False, error_message).to_dict())

        except KeyError:
            error_message = 'test_host_handler DELETE missing required element(s).'
            logger.debug(error_message)

        return JsonResponse(ReturnStatus(False, error_message).to_dict())


class BusinessAreaListView(ListView):
    model = BusinessArea
    template_name = 'business_area_list.html'


@require_http_methods(["POST", "DELETE"])
def business_area_handler(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if request.method == 'POST':
        data = json.loads(request.body)
        if pk is None:
            # New business area
            BusinessArea.objects.create(name=data['name'])
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())
        else:
            # existing business area update
            try:
                ba = BusinessArea.objects.get(pk=pk)
                ba.name = data['name']
                ba.save()
            except BusinessArea.DoesNotExist:
                return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())
    elif request.method == 'DELETE':
        try:
            ba = BusinessArea.objects.get(pk=pk)
            if ba.mission_set.all().count() != 0:
                return JsonResponse(ReturnStatus(False, 'Business Areas can not be deleted while missions are still associated with them.').to_dict())
            ba.delete()
        except BusinessArea.DoesNotExist:
            return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())
        return JsonResponse(ReturnStatus(True, 'OK').to_dict())


class ClassificationListView(ListView):
    model = ClassificationLegend
    template_name = 'classification_list.html'

    def get_context_data(self, **kwargs):
        context = super(ClassificationListView, self).get_context_data()
        context["available_colors"] = Color.objects.all()
        return context


@require_http_methods(["POST", "DELETE"])
def classification_handler(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if request.method == 'POST':
        data = json.loads(request.body)
        if pk is None:
            # New classification
            try:
                ClassificationLegend.objects.create(
                    verbose_legend=data['verbose_legend'],
                    short_legend=data['short_legend'],
                    text_color=Color.objects.get(pk=data['text_color']),
                    background_color=Color.objects.get(pk=data['background_color']),
                    report_label_color_selection=data['report_label_color_selection'],
                )
            except Color.DoesNotExist:
                return JsonResponse(ReturnStatus(False, 'One or more of the selected colors does not exist.').to_dict())
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())
        else:
            # existing classification update
            try:
                classification = ClassificationLegend.objects.get(pk=pk)
                classification.verbose_legend = data['verbose_legend']
                classification.short_legend = data['short_legend']
                classification.text_color = Color.objects.get(pk=data['text_color'])
                classification.background_color = Color.objects.get(pk=data['background_color'])
                classification.report_label_color_selection = data['report_label_color_selection']
                classification.save()

                # Ensure the legend cache is cleared
                legend_top_key = make_template_fragment_key('legend_partial_top')
                cache.delete(legend_top_key)
                legend_bottom_key = make_template_fragment_key('legend_partial_bottom')
                cache.delete(legend_bottom_key)

            except ClassificationLegend.DoesNotExist:
                return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())

    elif request.method == 'DELETE':
        try:
            classification = ClassificationLegend.objects.get(pk=pk)
            if classification == DARTDynamicSettings.objects.get_as_object().system_classification:
                return JsonResponse(ReturnStatus(False, 'Can not delete the classification the system is currently operating at. Change system classification and try again.').to_dict())
            classification.delete()

        except ClassificationLegend.DoesNotExist:
            return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())

        return JsonResponse(ReturnStatus(True, 'OK').to_dict())


class ColorListView(ListView):
    model = Color
    template_name = 'color_list.html'


@require_http_methods(["POST", "DELETE"])
def color_handler(request,*args, **kwargs):
    pk = kwargs.get('pk')
    if request.method == 'POST':
        data = json.loads(request.body)
        if pk is None:
            # New color
            try:
                Color.objects.create(
                    display_text=data['display_text'],
                    hex_color_code=data['hex_color_code'],
                )
            except Color.DoesNotExist:
                return JsonResponse(ReturnStatus(False, 'One or more of the selected colors does not exist.').to_dict())
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())
        else:
            # existing color update
            try:
                color = Color.objects.get(pk=pk)
                color.display_text = data['display_text']
                color.hex_color_code = data['hex_color_code']
                color.save()

                # Ensure the legend cache is cleared just in case this is a color update
                # to the active class label
                legend_top_key = make_template_fragment_key('legend_partial_top')
                cache.delete(legend_top_key)
                legend_bottom_key = make_template_fragment_key('legend_partial_bottom')
                cache.delete(legend_bottom_key)

            except Color.DoesNotExist:
                return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())
            return JsonResponse(ReturnStatus(True, 'OK').to_dict())

    elif request.method == 'DELETE':
        try:
            color = Color.objects.get(pk=pk)
            active_text_color = DARTDynamicSettings.objects.get_as_object().system_classification.text_color
            active_background_color = DARTDynamicSettings.objects.get_as_object().system_classification.background_color
            if color == active_text_color or color == active_background_color:
                return JsonResponse(ReturnStatus(False, 'Can not delete a color in use by the classification legend the system is currently operating at. Change system classification or color options and try again.').to_dict())
            color.delete()

        except Color.DoesNotExist:
            return JsonResponse(ReturnStatus(False, 'Key does not exist').to_dict())

        return JsonResponse(ReturnStatus(True, 'OK').to_dict())


class AboutTemplateView(TemplateView):
    template_name = "about.html"
