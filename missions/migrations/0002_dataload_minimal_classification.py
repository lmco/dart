# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
    Color = apps.get_model('missions', 'Color')
    black = Color.objects.create(display_text='Black', hex_color_code='000000')
    white = Color.objects.create(display_text='White', hex_color_code='ffffff')

    # Legends
    ClassificationLegend = apps.get_model('missions', 'ClassificationLegend')
    unrestricted = ClassificationLegend.objects.create(
        verbose_legend='UNRESTRICTED',
        short_legend='',
        text_color=white,
        background_color=black,
		report_label_color_selection='B',
    )

    # Create an initial (default) settings load
    DARTDynamicSettings = apps.get_model('missions', 'DARTDynamicSettings')

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
        ('missions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data, unload_data)
    ]
