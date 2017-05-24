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

from django.utils.text import normalize_newlines


def standardize_report_output_field(field_content):
    # Normalize newlines replaces \r\n from windows with \n
    standardized_text = normalize_newlines(field_content)

    # Replace blank fields with "N/A"
    if len(standardized_text) == 0:
        standardized_text = "N/A"

    return standardized_text


def join_as_compacted_paragraphs(paragraphs):
    """
    :param paragraphs: List containing individual paragraphs; potentially with extraneous whitespace within
    :return: String with \n separated paragraphs and no extra whitespace
    """

    paragraphs[:] = [' '.join(p.split()) for p in paragraphs]  # Remove extra whitespace & newlines

    return '\n'.join(paragraphs)
