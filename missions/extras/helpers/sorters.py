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

import logging
import json

from missions.models import Mission, TestDetail

logger = logging.getLogger(__name__)


class TestSortingHelper(object):

    @staticmethod
    def deconflict_and_update(mission_id, tests=None):
        """ Ensures the mission's testdetail_sort_order is accurate and returns an ordered array of current test Ids """

        logger.debug('Performing TC deconflict and update (mission {mission})'.format(mission=mission_id))

        mission_model = Mission.objects.get(pk=mission_id)
        sort_order = json.loads(mission_model.testdetail_sort_order)
        deconflicted_sort_order = []
        sort_order_dirty = False

        if not tests:
            try:
                tests = TestDetail.objects.filter(mission=mission_id)
            except TestDetail.DoesNotExist:
                tests = ()

        # If tests exist, but there's no sort order, this may be the first run of this DART version;
        # We should preserve existing sort order and build the testdetail_sort_order field
        if tests and not sort_order:
            logger.debug('TC Deconflict found TCs but no existing order (mission {mission}); ' +
                        'Building sort order from test case numbers'.format(mission=mission_id))
            tests.order_by('test_number')
            sort_order = [test.id for test in tests]

        # Perform a reconcile to catch edge cases where tests have been added or deleted
        logger.debug('TC Deconflict is reconciling sort order with the database (mission {mission})'
                    .format(mission=mission_id))
        test_ids_from_db = [test.id for test in tests]
        for x in sort_order:
            if x in test_ids_from_db:
                deconflicted_sort_order.append(x)
            else:
                logger.info('Sort order is dirty (TC has been deleted from DB) (mission {mission}, tc {tc})'
                            .format(mission=mission_id, tc=x))
                sort_order_dirty = True  # Id in mission's sort order, but not database (it's been deleted)

        for x in test_ids_from_db:
            if x not in deconflicted_sort_order:
                deconflicted_sort_order.append(x)
                logger.info('Sort order is dirty (TC has been added to DB) (mission {mission}, tc {tc})'
                            .format(mission=mission_id, tc=x))
                sort_order_dirty = True  # Id in the database, but not in the mission's sort order (it's been added)

        # Save the reconciled sort order
        if sort_order_dirty:
            mission_model.testdetail_sort_order = json.dumps(deconflicted_sort_order)
            mission_model.save(update_fields=['testdetail_sort_order'])
            logger.info('Reconciliation Performed (Mission %s): '
                        'Mission Sort Order: %s; '
                        'Database TC Records: %s; '
                        'Result of Deconflict: %s' % (mission_id, sort_order, test_ids_from_db, deconflicted_sort_order))

        return deconflicted_sort_order

    @classmethod
    def get_ordered_testdetails(cls, mission_id, reportable_tests_only=False):

        try:
            tests = TestDetail.objects.filter(mission=mission_id)
            if reportable_tests_only:
                tests = tests.filter(test_case_include_flag=True)
        except TestDetail.DoesNotExist:
            tests = ()

        sort_order = cls.deconflict_and_update(mission_id, tests)

        # Order
        test_dict = dict([(test.id, test) for test in tests])
        ordered_tests = [test_dict[test_id] for test_id in sort_order]

        return ordered_tests

