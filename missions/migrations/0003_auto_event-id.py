# Copyright 2024 Lockheed Martin Corporation
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


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("missions", "0002_dataload_minimal_classification"),
    ]

    operations = [
        migrations.AddField(
            model_name="mission",
            name="test_case_identifier",
            field=models.CharField(
                default=b"",
                max_length=20,
                verbose_name=b"Test Case Identifier",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="testdetail",
            name="re_eval_test_case_number",
            field=models.CharField(
                default=b"",
                help_text=b"Adds previous test case reference to description in report.",
                max_length=25,
                verbose_name=b"Re-Evaluate Test Case #",
                blank=True,
            ),
        ),
    ]
