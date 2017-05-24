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

from django import template

from missions.models import DARTDynamicSettings

register = template.Library()


@register.inclusion_tag('tags_managedata.html')
def manage_data_button(mission_id, testcase_id, number_of_attachments, as_button=False):
    """ Returns the text that should be displayed regarding attachments to a test case. """
    return {
        'mission_id': mission_id,
        'test_detail_id': testcase_id,
        'supporting_data_count': number_of_attachments,
        'as_button': as_button
    }

@register.inclusion_tag('tags_preloader_partial.html')
def preloader(align="center"):
    """
    Returns a quick preloader html snippet.
    :param align: string equal to "left", "center" (default), or "right"
    """
    return {
        'align': align,
    }

@register.inclusion_tag('tags_classification_legend_partial.html')
def legend_partial(location):
    """ Returns the top and bottom legend divs. """

    dynamic_settings_qryset = DARTDynamicSettings.objects.select_related(
        'system_classification',
        'system_classification__text_color',
        'system_classification__background_color',
    ).all()

    dynamic_settings = dynamic_settings_qryset.first()

    legend = dynamic_settings.system_classification

    return {
        'location': location,
        'classification_text_color': legend.text_color.hex_color_code,
        'classification_background_color': legend.background_color.hex_color_code,
        'classification_text': legend.verbose_legend,
    }
