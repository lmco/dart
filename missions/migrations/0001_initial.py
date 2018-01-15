# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import missions.models
import missions.extras.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationLegend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('verbose_legend', models.CharField(default=b'', max_length=200)),
                ('short_legend', models.CharField(default=b'', max_length=100)),
                ('report_label_color_selection', models.CharField(default=b'B', max_length=1, choices=[(b'T', b'Text Color'), (b'B', b'Back Color')])),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_text', models.CharField(default=b'', max_length=30)),
                ('hex_color_code', models.CharField(default=b'', max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='DARTDynamicSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host_output_format', models.CharField(default=b'{ip} ({name})', help_text=b'Use "{ip}" and "{name}" to specify how you want hosts to be displayed.', max_length=50, validators=[missions.extras.validators.validate_host_format_string])),
                ('system_classification', models.ForeignKey(to='missions.ClassificationLegend')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host_name', models.CharField(default=b'', max_length=100, blank=True)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('is_no_hit', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Mission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mission_name', models.CharField(max_length=255, verbose_name=b'Mission Name')),
                ('mission_number', models.CharField(max_length=5, verbose_name=b'Mission Number')),
                ('introduction', models.TextField(default=missions.models.introduction_default, verbose_name=b'Introduction', blank=True)),
                ('executive_summary', models.TextField(default=missions.models.executive_summary_default, verbose_name=b'Executive Summary', blank=True)),
                ('scope', models.TextField(default=missions.models.scope_default, verbose_name=b'Scope', blank=True)),
                ('objectives', models.TextField(default=missions.models.objectives_default, verbose_name=b'Objectives', blank=True)),
                ('technical_assessment_overview', models.TextField(default=missions.models.technical_assessment_overview_default, verbose_name=b'Technical Assessment / Attack Architecture Overview', blank=True)),
                ('conclusion', models.TextField(default=missions.models.conclusion_default, verbose_name=b'Conclusion', blank=True)),
                ('attack_phase_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Phases in report?')),
                ('attack_type_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Types in report?')),
                ('assumptions_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Assumptions in report?')),
                ('test_description_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Test Descriptions in report?')),
                ('findings_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Findings in report?')),
                ('mitigation_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Mitigations in report?')),
                ('tools_used_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Tools Used in report?')),
                ('command_syntax_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Command Syntaxes in report?')),
                ('targets_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Targets in report?')),
                ('sources_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Sources in report?')),
                ('attack_time_date_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Times in report?')),
                ('attack_side_effects_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Attack Side Effects in report?')),
                ('test_result_observation_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Test Details in report?')),
                ('supporting_data_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include Supporting Data Information in report?')),
                ('customer_notes_include_flag', models.BooleanField(default=True, verbose_name=b'Mission Option: Include customer notes section in report?')),
                ('testdetail_sort_order', models.TextField(default=b'[]', blank=True)),
                ('business_area', models.ForeignKey(verbose_name=b'Business Area', to='missions.BusinessArea')),
            ],
        ),
        migrations.CreateModel(
            name='SupportingData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.TextField(verbose_name=b'Caption', blank=True)),
                ('include_flag', models.BooleanField(default=True, verbose_name=b'Include attachment in report')),
                ('test_file', models.FileField(upload_to=b'', verbose_name=b'Supporting Data')),
            ],
        ),
        migrations.CreateModel(
            name='TestDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('test_number', models.IntegerField(default=0, verbose_name=b'Test Number')),
                ('test_case_include_flag', models.BooleanField(default=True, verbose_name=b'Include Test Case in report?')),
                ('test_case_status', models.CharField(default=b'NEW', max_length=100, verbose_name=b'Test Case Status', choices=[(b'NEW', b'Not started'), (b'IN_WORK', b'In work'), (b'REVIEW', b'Ready for review'), (b'FINAL', b'Approved / Final')])),
                ('enclave', models.CharField(max_length=100, verbose_name=b'Enclave Test Executed From', blank=True)),
                ('test_objective', models.CharField(help_text=b'Brief objective (ex.Port Scan against xyz)', max_length=255, verbose_name=b'Test Objective / Title')),
                ('attack_phase', models.CharField(max_length=20, verbose_name=b'Attack Phase', choices=[(b'RECON', b'Reconnaissance'), (b'WEP', b'Weaponization'), (b'DEL', b'Delivery'), (b'EXP', b'Exploitation'), (b'INS', b'Installation'), (b'C2', b'Command & Control'), (b'AOO', b'Actions on Objectives')])),
                ('attack_phase_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Phase in report?')),
                ('attack_type', models.CharField(help_text=b'Example: SYN flood, UDP flood, malformed packets, web, fuzz, etc.', max_length=255, verbose_name=b'Attack Type', blank=True)),
                ('attack_type_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Type in report?')),
                ('assumptions', models.TextField(help_text=b'Example: Attacker has a presence in xyz segment, etc.', verbose_name=b'Assumptions', blank=True)),
                ('assumptions_include_flag', models.BooleanField(default=True, verbose_name=b'Include Assumptions in report?')),
                ('test_description', models.TextField(help_text=b'Describe test case to be performed, what is the objective of this test case (Is it to deny, disrupt, penetrate, modify etc.)', verbose_name=b'Description', blank=True)),
                ('test_description_include_flag', models.BooleanField(default=True, verbose_name=b'Include Test Description in report?')),
                ('sources_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Sources in report?')),
                ('targets_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Targets in report?')),
                ('attack_time_date', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Date/time attack was launched', verbose_name=b'Attack Date / Time', blank=True)),
                ('attack_time_date_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Time in report?')),
                ('tools_used', models.TextField(help_text=b'Example: Burp Suite, Wireshark, NMap, etc.', verbose_name=b'Tools Used', blank=True)),
                ('tools_used_include_flag', models.BooleanField(default=True, verbose_name=b'Include Tools Used in report?')),
                ('command_syntax', models.TextField(help_text=b'Include sample command/syntax used if possible. If a script was used/created, what commands will run it?', verbose_name=b'Command/Syntax', blank=True)),
                ('command_syntax_include_flag', models.BooleanField(default=True, verbose_name=b'Include Command Syntax in report?')),
                ('test_result_observation', models.TextField(help_text=b'Example: An average of 8756 SYN-ACK/sec were received at the attack laptop over the 30 second attack period. Plots of traffic flows showed degradation of all flow performance during time 5s \xe2\x80\x93 40s after which they recovered.', verbose_name=b'Test Result Details', blank=True)),
                ('test_result_observation_include_flag', models.BooleanField(default=True, verbose_name=b'Include Test Result in report?')),
                ('attack_side_effects', models.TextField(help_text=b'List any observed side effects, if any. Example: Firewall X froze and subsequently crashed.', verbose_name=b'Attack Side Effects', blank=True)),
                ('attack_side_effects_include_flag', models.BooleanField(default=True, verbose_name=b'Include Attack Side Effects in report?')),
                ('execution_status', models.CharField(default=b'N', help_text=b'Execution status of the test case.', max_length=2, verbose_name=b'Execution Status', choices=[(b'N', b'Not Run'), (b'R', b'Run'), (b'C', b'Cancelled'), (b'NA', b'N/A')])),
                ('has_findings', models.BooleanField(default=False)),
                ('findings', models.TextField(help_text=b'Document the specific finding related to this test or against the main test objectives if applicable', verbose_name=b'Findings', blank=True)),
                ('findings_include_flag', models.BooleanField(default=True, verbose_name=b'Include Findings in report?')),
                ('mitigation', models.TextField(help_text=b'Example: Configure xyz, implement xyz, etc.', verbose_name=b'Mitigation', blank=True)),
                ('mitigation_include_flag', models.BooleanField(default=True, verbose_name=b'Include Mitigations in report?')),
                ('point_of_contact', models.CharField(default=b'', help_text=b'Individual working or most familiar with this test case.', max_length=20, verbose_name=b'POC', blank=True)),
                ('mission', models.ForeignKey(verbose_name=b'Mission', to='missions.Mission')),
                ('source_hosts', models.ManyToManyField(related_name='source_set', to='missions.Host')),
                ('target_hosts', models.ManyToManyField(related_name='target_set', to='missions.Host')),
            ],
        ),
        migrations.AddField(
            model_name='supportingdata',
            name='test_detail',
            field=models.ForeignKey(verbose_name=b'Test Details', to='missions.TestDetail'),
        ),
        migrations.AddField(
            model_name='host',
            name='mission',
            field=models.ForeignKey(to='missions.Mission'),
        ),
        migrations.AddField(
            model_name='classificationlegend',
            name='background_color',
            field=models.ForeignKey(related_name='classificationlegend_background_set', to='missions.Color'),
        ),
        migrations.AddField(
            model_name='classificationlegend',
            name='text_color',
            field=models.ForeignKey(related_name='classificationlegend_text_set', to='missions.Color'),
        ),
    ]
