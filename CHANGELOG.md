<!--
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
-->

# Changelog

>All notable changes to this project will be documented in this file.
>
>The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<hr>

## [Unreleased]

### Added

* Edit-conflict protection — optimistic locking on `Mission` and `TestDetail`. An edit is rejected with a warning if another user saved first (last-person-to-save no longer silently wins).
* Mission export / import ("mission package") — download a mission (hosts, test cases with source/target links, and supporting-data metadata) as a portable JSON document, and restore it via `python manage.py import_mission <file.json>`. Binary attachments are copied separately.
* Per-test audit trail — a `ChangeLog` model records who changed a mission / test case and when (create, update, delete, clone, host add/update/delete, import), shown as a history panel on the edit pages.
* Clone an entire mission — duplicates a mission plus its hosts, test cases, and supporting data (test statuses reset to "Not started") from the mission list.
* Login-interstitial middleware (`RequiredInterstitial`) is now wired into `MIDDLEWARE` and activates when `REQUIRED_INTERSTITIAL_DISPLAY_INTERVAL` is configured; previously it was dormant and would not have loaded on Django 3.x.

### Changed

* `Host.get_absolute_url()` now resolves to the mission's hosts page instead of returning `None`.
* Host display formatting is memoized with an invalidation hook instead of a 5-minute cache, so format changes apply immediately and missing system settings fall back to a safe default.

### Fixed

* Interstitial middleware imported `django.core.urlresolvers`, which does not exist on Django 3.x and would have caused an `ImportError` if enabled; now uses `django.urls` and `MiddlewareMixin`.
* Report (`.docx`) and supporting-data downloads now use correct content types instead of `text/plain`.
* Report attachment zip generation no longer leaves temporary `SUPPORTING_DATA_PACKAGE/` snapshots behind.


## [v2.1.2] - 2026-01-08

### Changed

* Closed environment installation instructions
* Dependencies update


## [v2.1.1] - 2024-04-25

### Changed

* Django version 3.2.25
* README copyright year


## [v2.1.0] - 2024-03-01

### Added

* Changelog file 

### Changed

* Python version >=3.9
* Local installation process update

### Fixed

* Docker build process
