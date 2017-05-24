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

from __future__ import division
from collections import Counter, defaultdict

import logging

from missions.models import TestDetail

logger = logging.getLogger(__name__)


class MissionAnalytics(object):

    def __init__(self, mission_id):
        self.mission_id = mission_id

        # All analytics exclude hidden test cases so we don't report
        # numbers of tests greater than what the customer ultimately sees
        self.testcases = TestDetail.objects.filter(mission=self.mission_id).exclude(test_case_include_flag=False)

        self.test_case_types_by_mission_week = self._count_of_test_case_types_by_mission_week()

    def count_of_findings(self):
        count = self.testcases.exclude(findings=u'').count()
        return count

    def count_of_test_cases(self):
        count = self.testcases.count()
        return count

    def count_of_executed_test_cases(self):
        count = self.testcases.exclude(execution_status=u'N').count()
        return count

    def count_of_test_cases_approved(self):
        count = self.testcases.filter(test_case_status=u'FINAL').count()
        return count

    def mission_execution_percentage(self):

        if self.count_of_test_cases() == 0:
            # prevent division by 0
            percentage = 0
        else:
            percentage = self.count_of_executed_test_cases() / self.count_of_test_cases()
        return '{:.0%}'.format(percentage)

    def mission_completion_percentage(self):

        if self.count_of_test_cases() == 0:
            # prevent division by 0
            percentage = 0
        else:
            percentage = self.count_of_test_cases_approved() / self.count_of_test_cases()
        return '{:.0%}'.format(percentage)

    def count_of_test_cases_by_result(self):
        """
        Summation of test cases which have each result type.
        :return: A list containing 2 lists:
                    - a list of test result type identifiers
                    - an identical length list of integer quantities of TCs which have the corresponding result
        """

        # Get the test result type tuple & convert to list
        output_list = [[], [], []]  # Lookup value list, Display text list, Count list

        def nested_tuple_to_shallow_list(tup):
            output_list[0].append(tup[0])
            output_list[1].append(tup[1])
            output_list[2].append(0)

        for result in TestDetail.EXECUTION_STATUS_OPTIONS:
            nested_tuple_to_shallow_list(result)

        for tc_result in self.testcases.values('execution_status'):
            index = output_list[0].index(tc_result['execution_status'])
            output_list[2][index] += 1

        return output_list[1:]  # No need to return the lookup values list

    def count_of_test_cases_by_mission_week(self):
        """
        Counts total test cases executed per week.
        :return: A zero-indexed list of the number of test cases executed per week.
        """

        if self.count_of_executed_test_cases() == 0:
            return [0]

        # Get the execution date for each test case in the mission
        tc_dates = self.testcases.exclude(execution_status=u'N').values('attack_time_date')

        # Create a hashmap of the count of TCs per iso calendar week
        weekly_count = Counter()
        for tc_date in tc_dates:
            isocalendar_week = tc_date['attack_time_date'].isocalendar()[1]  # Grab the isocalendar Week #
            weekly_count[isocalendar_week] += 1

        # Get the lowest & highest key values - these are week 1 and the last week respectively
        # This allows for skipped weeks (just in case)
        first_week = min(weekly_count.keys())
        last_week = max(weekly_count.keys())
        week_delta = last_week - first_week + 1

        # Build a hashmap of week # and the associated count
        zero_indexed_weekly_count = [0] * week_delta
        for week, count in weekly_count.items():
            zero_indexed_weekly_count[week - first_week] = count

        return zero_indexed_weekly_count

    def _count_of_test_case_types_by_mission_week(self):
        """
        Weekly totals broken out by attack phase; includes total row.
        :return: A list of lists: Each list within the containing list is guaranteed to be the same length as all others
                 and will have the test case Phase at index 0, followed by the number of test cases of that type
                 completed each week of the mission's execution. The last inner list is a total row.
                 Example of 2 week execution:
                 [['R&D', 2, 0],['EXP', 1, 2],['TOTAL', 3, 2]]
        """

        if self.count_of_executed_test_cases() == 0:
            return [['No TCs have been executed yet!']]

        # Get the execution date & type for each executed test case in the mission
        tc_records = self.testcases.exclude(execution_status=u'N').values('attack_time_date', 'attack_phase')

        # Create a hashmap of the count of TCs per iso calendar week
        weekly_count = defaultdict(Counter)

        for tc_record in tc_records:
            isocalendar_week = tc_record['attack_time_date'].isocalendar()[1]  # Grab the isocalendar Week #
            attack_phase = tc_record['attack_phase']
            weekly_count[isocalendar_week][attack_phase] += 1

        # Get the lowest & highest key values - these are week 1 and the last week respectively
        # This allows for skipped weeks (just in case)
        first_week = min(weekly_count.keys())
        last_week = max(weekly_count.keys())
        week_delta = last_week - first_week + 1

        # Build a hashmap of week # and the associated count
        zero_indexed_phase_count_by_week = []

        header_row = list()
        header_row.append('')
        header_row.extend(range(1, week_delta))

        total_row = list()
        total_row.append('TOTAL')
        total_row.extend([0] * week_delta)

        for phase_tuple in TestDetail.ATTACK_PHASES:
            phase = phase_tuple[0]
            phase_row = [0] * (week_delta + 1)
            phase_row[0] = phase
            for week, attack_phase_counter in weekly_count.items():
                column = week - first_week + 1
                phase_row[column] = attack_phase_counter[phase]
                total_row[column] += attack_phase_counter[phase]
            zero_indexed_phase_count_by_week.append(phase_row)

        zero_indexed_phase_count_by_week.append(total_row)

        logger.debug(zero_indexed_phase_count_by_week)

        return zero_indexed_phase_count_by_week

    def count_of_test_case_types_by_mission_week(self):
        return self.test_case_types_by_mission_week
