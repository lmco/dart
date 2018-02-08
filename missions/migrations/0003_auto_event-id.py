# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0002_dataload_minimal_classification'),
    ]

    operations = [
        migrations.AddField(
            model_name='mission',
            name='test_case_identifier',
            field=models.CharField(default=b'', max_length=20, verbose_name=b'Test Case Identifier', blank=True),
        ),
        migrations.AddField(
            model_name='testdetail',
            name='re_eval_test_case_number',
            field=models.CharField(default=b'', help_text=b'Adds previous test case reference to description in report.', max_length=25, verbose_name=b'Re-Evaluate Test Case #', blank=True),
        ),
    ]
