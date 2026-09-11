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

# -*- coding: utf-8 -*-
# Generated manually for feature additions: edit-conflict version fields + audit trail (ChangeLog)


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0005_auto_20230708_1306'),
    ]

    operations = [
        # Optimistic-concurrency guards for edit-conflict protection
        migrations.AddField(
            model_name='mission',
            name='version',
            field=models.IntegerField(default=0, verbose_name='Version'),
        ),
        migrations.AddField(
            model_name='testdetail',
            name='version',
            field=models.IntegerField(default=0, verbose_name='Version'),
        ),
        # Audit trail
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('mission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to='missions.mission')),
                ('test_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changelogs', to='missions.testdetail')),
            ],
        ),
    ]