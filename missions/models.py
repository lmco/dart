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

import os

from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

from extras.helpers.formatters import join_as_compacted_paragraphs
from extras.validators import validate_host_format_string


"""
Defaults
Python 2 can't serialize unbound method functions, therefore these defaults are declared here.
"""


def introduction_default():
    return Mission.get_default_text('introduction.txt')


def executive_summary_default():
    return Mission.get_default_text('executive_summary.txt')


def scope_default():
    return Mission.get_default_text('scope.txt')


def objectives_default():
    return Mission.get_default_text('objectives.txt')


def technical_assessment_overview_default():
    return Mission.get_default_text('technical_assessment.txt')


def conclusion_default():
    return Mission.get_default_text('conclusion.txt')


"""
Models
"""


class Mission(models.Model):

    @staticmethod
    def get_default_text(file_name):
        TEMPALTE_DIR = os.path.join(settings.BASE_DIR, 'templates')
        with open(os.path.join(TEMPALTE_DIR, file_name), 'r') as template:
            output = join_as_compacted_paragraphs(template.readlines())
            return output

    # Model Fields

    mission_name = models.CharField(
        max_length=255,
        verbose_name="Mission Name",
    )

    mission_number = models.CharField(
        max_length=5,
        verbose_name="Mission Number",
    )

    test_case_identifier = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Test Case Identifier",
    )

    business_area = models.ForeignKey(
        'BusinessArea',
        verbose_name="Business Area",
    )

    introduction = models.TextField(
        blank=True,
        verbose_name="Introduction",
        default=introduction_default,
    )

    executive_summary = models.TextField(
        blank=True,
        verbose_name="Executive Summary",
        default=executive_summary_default
    )

    scope = models.TextField(
        blank=True,
        verbose_name="Scope",
        default=scope_default
    )

    objectives = models.TextField(
        blank=True,
        verbose_name="Objectives",
        default=objectives_default
    )

    technical_assessment_overview = models.TextField(
        blank=True,
        verbose_name="Technical Assessment / Attack Architecture Overview",
        default=technical_assessment_overview_default
    )

    conclusion = models.TextField(
        blank=True,
        verbose_name="Conclusion",
        default=conclusion_default
    )

    # Mission-wide reporting include flags
    attack_phase_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Phases in report?",
    )

    attack_type_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Types in report?",
    )

    assumptions_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Assumptions in report?",
    )

    test_description_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Test Descriptions in report?",
    )

    findings_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Findings in report?",
    )

    mitigation_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Mitigations in report?",
    )

    tools_used_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Tools Used in report?",
    )

    command_syntax_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Command Syntaxes in report?",
    )

    targets_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Targets in report?",
    )

    sources_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Sources in report?",
    )

    attack_time_date_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Times in report?",
    )

    attack_side_effects_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Attack Side Effects in report?",
    )

    test_result_observation_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Test Details in report?",
    )

    supporting_data_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include Supporting Data Information in report?"
    )

    customer_notes_include_flag = models.BooleanField(
        default=True,
        verbose_name="Mission Option: Include customer notes section in report?"
    )

    testdetail_sort_order = models.TextField(
        blank=True,
        default="[]"
    )

    def __str__(self):
        return "%s (%s)" % (self.mission_name, self.mission_number)


class Host(models.Model):
    mission = models.ForeignKey(
        Mission
    )

    host_name = models.CharField(
        blank=True,
        default="",
        max_length=100,
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    is_no_hit = models.BooleanField(
        default=False,
    )

    @staticmethod
    def get_host_output_format_string():
        format_string = str(DARTDynamicSettings.objects.get_as_object().host_output_format)
        return format_string

    def __str__(self):
        format_string = cache.get('host_output_format_string')
        if format_string is None:
            cache.set('host_output_format_string', Host.get_host_output_format_string(), 300)
            format_string = cache.get('host_output_format_string')
        return format_string.format(name=self.host_name, ip=self.ip_address)

    def get_absolute_url(self):
        return


class TestDetail(models.Model):
    mission = models.ForeignKey(Mission, verbose_name="Mission")

    test_number = models.IntegerField(
        blank=False,
        verbose_name="Test Number",
        default=0
    )

    test_case_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Test Case in report?"
    )

    TEST_CASE_STATUSES = (
        ('NEW', 'Not started'),
        ('IN_WORK', 'In work'),
        ('REVIEW', 'Ready for review'),
        ('FINAL', 'Approved / Final'),
    )

    test_case_status = models.CharField(
        choices=TEST_CASE_STATUSES,
        max_length=100,
        verbose_name="Test Case Status",
        default='NEW',
    )

    enclave = models.CharField(
        blank=True,
        max_length=100,
        verbose_name='Enclave Test Executed From'
    )

    test_objective = models.CharField(
        blank=False,
        max_length=255,
        verbose_name="Test Objective / Title",
        help_text="Brief objective (ex.Port Scan against xyz)",
    )

    # Note: Attack Phases based on the Lockheed Martin Kill Chain(R)
    ATTACK_PHASES = (
        ('RECON', 'Reconnaissance'),
        ('WEP', 'Weaponization'),
        ('DEL', 'Delivery'),
        ('EXP', 'Exploitation'),
        ('INS', 'Installation'),
        ('C2', 'Command & Control'),
        ('AOO', 'Actions on Objectives'),
    )

    attack_phase = models.CharField(
        choices=ATTACK_PHASES,
        max_length=20,
        verbose_name="Attack Phase",
    )

    attack_phase_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Phase in report?",
    )

    attack_type = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="Attack Type",
        help_text="Example: SYN flood, UDP flood, malformed packets, web, fuzz, etc.",
    )

    attack_type_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Type in report?",
    )

    assumptions = models.TextField(
        blank=True,
        verbose_name="Assumptions",
        help_text="Example: Attacker has a presence in xyz segment, etc."
    )

    assumptions_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Assumptions in report?",
    )

    test_description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Describe test case to be performed, what is the objective of this test case (Is it to deny, disrupt, penetrate, modify etc.)"
    )

    test_description_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Test Description in report?",
    )

    source_hosts = models.ManyToManyField(
        'Host',
        related_name='source_set',
    )

    sources_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Sources in report?",
    )

    target_hosts = models.ManyToManyField(
        'Host',
        related_name='target_set',
    )

    targets_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Targets in report?",
    )

    attack_time_date = models.DateTimeField(
        blank=True,
        default=timezone.now,
        verbose_name="Attack Date / Time",
        help_text="Date/time attack was launched"
    )

    attack_time_date_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Time in report?",
    )

    tools_used = models.TextField(
        blank=True,
        verbose_name="Tools Used",
        help_text="Example: Burp Suite, Wireshark, NMap, etc."
    )

    tools_used_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Tools Used in report?",
    )

    command_syntax = models.TextField(
        blank=True,
        verbose_name="Command/Syntax",
        help_text="Include sample command/syntax used if possible. If a script was used/created, what commands will run it?"
    )

    command_syntax_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Command Syntax in report?",
    )

    test_result_observation = models.TextField(
        blank=True,
        verbose_name="Test Result Details",
        help_text="Example: An average of 8756 SYN-ACK/sec were received at the attack laptop over the 30 second attack "
                  "period. Plots of traffic flows showed degradation of all flow performance during time 5s – 40s "
                  "after which they recovered."
    )

    test_result_observation_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Test Result in report?",
    )

    attack_side_effects = models.TextField(
        blank=True,
        verbose_name="Attack Side Effects",
        help_text="List any observed side effects, if any. Example: Firewall X froze and subsequently crashed."
    )

    attack_side_effects_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Attack Side Effects in report?",
    )

    EXECUTION_STATUS_OPTIONS = (
        ('N', 'Not Run'),
        ('R', 'Run'),
        ('C', 'Cancelled'),
        ('NA', 'N/A'),
    )

    execution_status = models.CharField(
        choices=EXECUTION_STATUS_OPTIONS,
        max_length=2,
        verbose_name="Execution Status",
        default='N',
        help_text="Execution status of the test case."
    )

    has_findings = models.BooleanField(
        default=False,
    )

    findings = models.TextField(
        blank=True,
        verbose_name="Findings",
        help_text="Document the specific finding related to this test or against the main test objectives if applicable"
    )

    findings_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Findings in report?",
    )

    mitigation = models.TextField(
        blank=True,
        verbose_name="Mitigation",
        help_text="Example: Configure xyz, implement xyz, etc."
    )

    mitigation_include_flag = models.BooleanField(
        default=True,
        verbose_name="Include Mitigations in report?",
    )

    point_of_contact = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="POC",
        help_text="Individual working or most familiar with this test case."
    )

    re_eval_test_case_number = models.CharField(
        max_length=25,
        blank=True,
        default="",
        verbose_name="Re-Evaluate Test Case #",
        help_text="Adds previous test case reference to description in report."
    )

    supporting_data_sort_order = models.TextField(
        blank=True,
        default="[]"
    )

    def count_of_supporting_data(self):
        return len(SupportingData.objects.filter(test_detail=self.pk))

    def __str__(self):
        return "%s (%s)" % (self.test_objective, self.id)

    def save(self, *args, **kwargs):
        self.has_findings = True if len(self.findings) > 0 else False
        return super(TestDetail, self).save(*args, **kwargs)


class SupportingData(models.Model):
    test_detail = models.ForeignKey(TestDetail, verbose_name="Test Details")

    caption = models.TextField(
        blank=True,
        verbose_name="Caption",
    )

    include_flag = models.BooleanField(
        default=True,
        verbose_name="Include attachment in report"
    )

    test_file = models.FileField(
        verbose_name="Supporting Data"
    )

    def filename(self):
        return os.path.basename(self.test_file.name)

    def get_absolute_url(self):
        return reverse_lazy('data-view', {'supportingdata': self.pk})


class BusinessArea(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name


class Color(models.Model):
    display_text = models.CharField(
        blank=False,
        max_length=30,
        default="",
    )

    hex_color_code = models.CharField(
        blank=False,
        max_length=6,
        default="",
    )

    def __str__(self):
        return '{0.display_text}'.format(self)


class ClassificationLegend(models.Model):
    verbose_legend = models.CharField(
        blank=False,
        max_length=200,
        default="",
    )

    short_legend = models.CharField(
        blank=False,
        max_length=100,
        default="",
    )

    text_color = models.ForeignKey(
        'Color',
        related_name='classificationlegend_text_set',
    )

    background_color = models.ForeignKey(
        'Color',
        related_name='classificationlegend_background_set',
    )

    REPORT_LABEL_COLOR_OPTIONS = (
        ('T', 'Text Color'),
        ('B', 'Back Color'),
    )

    report_label_color_selection = models.CharField(
        choices=REPORT_LABEL_COLOR_OPTIONS,
        max_length=1,
        default='B',
        blank=False,
    )

    def get_report_label_color(self):
        if self.report_label_color_selection == 'T':
            return self.text_color
        else:
            return self.background_color

    def __str__(self):
        return '{0.verbose_legend} ({0.short_legend})'.format(self)


class DARTDynamicSettingsManager(models.Manager):
    # This manager is used to ensure we only have one instance of system-wide dynamic settings and instantiates it if
    # it does not exist

    def get_as_queryset(self):
        queryset = DARTDynamicSettings.objects.all()
        if not queryset:
            DARTDynamicSettings.objects.create()
            queryset = DARTDynamicSettings.objects.all()
        return queryset

    def get_as_object(self):
        return self.get_as_queryset().first()


class DARTDynamicSettings(models.Model):
    system_classification = models.ForeignKey(
        'ClassificationLegend',
    )

    host_output_format = models.CharField(
        max_length=50,
        default='{ip} ({name})',
        help_text='Use "{ip}" and "{name}" to specify how you want hosts to be displayed.',
        validators=[validate_host_format_string]
    )

    # Since we're treating Dynamic Settings as a singleton,
    # override the default manager to enforce this
    objects = DARTDynamicSettingsManager()


# Catch deletions of supporting data records and remove the associated file
@receiver(post_delete, sender=SupportingData)
def SupportingData_delete(sender, instance, **kwargs):
    instance.test_file.delete(False)
