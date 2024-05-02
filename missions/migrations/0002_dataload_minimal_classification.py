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


from django.db import migrations

"""
This migration loads the bare minimum data to missions.Color and missions.ClassificationLegend for the application
to operate. Failure to run this migration will (probably) result in devastating application errors.

More colors and classifications can be loaded for you from the included common_classifications fixture:

python manage.py loaddata common_classifications

(Or you can just run `python /install/offline/setup.py` and they'll be added for you)
"""


def load_data(apps, schema_editor):
    # Colors
    Color = apps.get_model("missions", "Color")
    black = Color.objects.create(display_text="Black", hex_color_code="000000")
    white = Color.objects.create(display_text="White", hex_color_code="ffffff")

    # Legends
    ClassificationLegend = apps.get_model("missions", "ClassificationLegend")
    unrestricted = ClassificationLegend.objects.create(
        verbose_legend="UNRESTRICTED",
        short_legend="",
        text_color=white,
        background_color=black,
        report_label_color_selection="B",
    )

    # Create an initial (default) settings load
    DARTDynamicSettings = apps.get_model("missions", "DARTDynamicSettings")

    qryset = DARTDynamicSettings.objects.all()

    if not qryset:
        DARTDynamicSettings.objects.create(
            system_classification=unrestricted,
        )


def unload_data(apps, schema_editor):
    # This migration does not support unloading
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("missions", "0001_initial"),
    ]

    operations = [migrations.RunPython(load_data, unload_data)]
