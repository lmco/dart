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

"""
Mission export/import ("mission package").

Serializes a Mission's full structure (scalars, hosts, test cases with source/target
links, supporting-data metadata) to a portable JSON document, and reconstructs a fresh
copy from that document.

Binary supporting-data files are NOT embedded in the JSON — the document lists their
relative filenames (``files``) so the operator knows which files to copy alongside it;
``import_mission_from_dict`` links a supporting-data record only if the file already
exists under MEDIA_ROOT.
"""

import json
import logging
import os

from django.conf import settings
from django.utils import timezone

from missions.models import Mission, Host, TestDetail, SupportingData
from missions.extras.helpers.sorters import TestSortingHelper

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

# When round-tripping, these fields are re-derived rather than copied verbatim.
_SKIP_MISSION_FIELDS = {'id', 'version'}
_SKIP_HOST_FIELDS = {'id'}
_SKIP_TEST_FIELDS = {'id', 'version', 'source_hosts', 'target_hosts'}
_SKIP_DATA_FIELDS = {'id'}


def _scalar_fields(instance, skip):
    out = {}
    for field in instance._meta.fields:
        if field.name in skip:
            continue
        out[field.name] = getattr(instance, field.name)
    return out


def _jsonify(value):
    """Make the payload JSON-safe (datetimes/None handled via default=str)."""
    return json.loads(json.dumps(value, default=str))


def export_mission_to_dict(mission):
    """
    :param mission: A Mission instance (with related objects accessible).
    :return: A plain-dict (JSON-safe) representation of the mission package.
    """
    # Assign each host/test a deterministic package id: its list index, so M2M refs
    # stay stable across import.
    host_pkg_id = {}
    test_pkg_id = {}

    hosts = []
    for host in mission.host_set.all().order_by('id'):
        host_pkg_id[host.id] = len(hosts)
        hosts.append(_scalar_fields(host, _SKIP_HOST_FIELDS))

    tests = []
    files = set()
    for test in TestSortingHelper.get_ordered_testdetails(mission.id):
        test_pkg_id[test.id] = len(tests)
        data = _scalar_fields(test, _SKIP_TEST_FIELDS)
        data['source_host_ids'] = [host_pkg_id[h.id] for h in test.source_hosts.all().order_by('id')]
        data['target_host_ids'] = [host_pkg_id[h.id] for h in test.target_hosts.all().order_by('id')]
        data['supporting_data'] = []
        for sd in TestSortingHelper.get_ordered_supporting_data(test.id):
            data['supporting_data'].append(_scalar_fields(sd, _SKIP_DATA_FIELDS))
            fname = os.path.basename(sd.test_file.name)
            if fname:
                files.add(fname)
        tests.append(data)

    result = _scalar_fields(mission, _SKIP_MISSION_FIELDS)
    result['model'] = 'mission'
    result['schema_version'] = SCHEMA_VERSION
    result['exported_at'] = timezone.now()
    result['hosts'] = hosts
    result['tests'] = tests
    result['files'] = sorted(files)

    return _jsonify(result)


def export_mission_json(mission):
    return json.dumps(export_mission_to_dict(mission), indent=2, sort_keys=True)


def import_mission_from_dict(data, user=None):
    """
    Reconstruct a fresh Mission (new ids) from an exported package dict.

    :param data: dict as produced by :func:`export_mission_to_dict`.
    :param user: optional user to attach to the 'imported' audit record.
    :return: The newly created Mission.
    :raises ValueError: if the payload is malformed or has a mismatched schema.
    """
    if data.get('model') != 'mission':
        raise ValueError("Not a mission package (missing 'model' == 'mission').")
    if data.get('schema_version') != SCHEMA_VERSION:
        raise ValueError("Unsupported package schema_version: %s (expected %s)." %
                         (data.get('schema_version'), SCHEMA_VERSION))
    if 'tests' not in data or 'hosts' not in data:
        raise ValueError("Mission package is missing 'hosts'/'tests' sections.")

    # Lazy import to avoid a circular import at module load.
    from missions.extras.audit import log_change

    # ---- Mission ----
    mission_scalars = {k: v for k, v in data.items()
                       if k not in _SKIP_MISSION_FIELDS
                       and k not in ('model', 'schema_version', 'exported_at',
                                     'hosts', 'tests', 'files')}
    mission = Mission.objects.create(**mission_scalars)
    # Default to empty sort order; rebuilt below if the package had one.
    mission.testdetail_sort_order = '[]'
    mission.save(update_fields=['testdetail_sort_order'])

    # ---- Hosts (must exist before tests can reference them via M2M) ----
    host_map = {}  # package host id (list index) -> new db host id
    for idx, host_data in enumerate(data.get('hosts', [])):
        host_scalars = {k: v for k, v in host_data.items() if k not in _SKIP_HOST_FIELDS}
        host = Host.objects.create(mission=mission, **host_scalars)
        host_map[idx] = host.pk

    # ---- Tests + supporting data ----
    test_map = {}  # package test id (list index) -> new db test id
    test_data_sort_order = {}  # new test id -> (old order string, old-id->new-id dict)
    for idx, test_data in enumerate(data.get('tests', [])):
        test_scalars = {k: v for k, v in test_data.items()
                        if k not in _SKIP_TEST_FIELDS
                        and k not in ('source_host_ids', 'target_host_ids',
                                      'supporting_data')}
        # Fresh imports always reset lifecycle state
        test_scalars['test_case_status'] = 'NEW'
        test_scalars.pop('has_findings', None)  # recomputed by save()
        # Start with empty sort order; rebuilt after supporting data is created.
        old_order_str = test_scalars.pop('supporting_data_sort_order', '[]') or '[]'
        test_scalars['supporting_data_sort_order'] = '[]'

        test = TestDetail.objects.create(mission=mission, **test_scalars)
        test_map[idx] = test.pk

        source_new = [host_map[h] for h in test_data.get('source_host_ids', []) if h in host_map]
        target_new = [host_map[t] for t in test_data.get('target_host_ids', []) if t in host_map]
        test.source_hosts.set(source_new)
        test.target_hosts.set(target_new)

        # Supporting-data linking: only if the file is present under MEDIA_ROOT.
        # Old data ids are the export index within this test's list; new ids are the
        # returned SupportingData rows, so we can build an old->new id map.
        data_id_map = {}
        for data_idx, sd_data in enumerate(test_data.get('supporting_data', [])):
            fname = os.path.basename(sd_data.get('test_file', '') or '')
            file_path = os.path.join(settings.MEDIA_ROOT, fname)
            if fname and not os.path.isfile(file_path):
                logger.warning('Supporting data file missing; skipping: %s', file_path)
                continue
            new_data = SupportingData.objects.create(
                test_detail=test,
                caption=sd_data.get('caption', ''),
                include_flag=sd_data.get('include_flag', True),
                test_file=sd_data.get('test_file', '') or '',
            )
            data_id_map[data_idx] = new_data.pk

        test_data_sort_order[test.pk] = (old_order_str, data_id_map)

    # ---- Rebuild sort orders (after all supporting data records exist) ----
    _rebuild_mission_sort_order(mission, data, test_map)
    _rebuild_test_sort_orders(test_data_sort_order)

    log_change(user=user, mission=mission, action='imported',
               description='Imported from mission package (schema v%s)' % SCHEMA_VERSION)

    return mission


def _rebuild_mission_sort_order(mission, data, test_map):
    """Mission.testdetail_sort_order was exported as old test ids; map to new ids."""
    try:
        old_order = json.loads(data.get('testdetail_sort_order') or '[]')
    except (TypeError, ValueError):
        old_order = []
    new_order = [test_map[i] for i in old_order if i in test_map]
    # Include any tests the package had that were missing from the sort order.
    new_order += [v for k, v in test_map.items() if v not in new_order]
    mission.testdetail_sort_order = json.dumps(new_order)
    mission.save(update_fields=['testdetail_sort_order'])


def _rebuild_test_sort_orders(test_data_sort_order):
    """Remap each test's supporting_data_sort_order from old data ids to new ids."""
    for new_test_id, (old_order_str, data_id_map) in test_data_sort_order.items():
        try:
            old_order = json.loads(old_order_str or '[]')
        except (TypeError, ValueError):
            old_order = []
        # Map each old data id to its newly-created id; keep only present ones.
        new_order = [data_id_map[i] for i in old_order if i in data_id_map]
        TestDetail.objects.filter(pk=new_test_id).update(
            supporting_data_sort_order=json.dumps(new_order))