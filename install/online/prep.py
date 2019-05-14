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

import argparse
import os
import subprocess
import urllib2
import ssl
import socket
import logging

"""
DART Offline Installation Preparation

Use this file to gather the dependencies required for offline installation.
"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

ONLINE_DIR = os.path.dirname(os.path.realpath(__file__))
INSTALL_DIR, _ = os.path.split(ONLINE_DIR)
OFFLINE_DIR = os.path.join(INSTALL_DIR, 'offline')
BASE_DIR, _ = os.path.split(INSTALL_DIR)
DOWNLOADS_DIR = os.path.join(OFFLINE_DIR, 'downloads')


class DartOfflinePrepper(object):

    def __init__(self, *args, **kwargs):

        self.PROXY = kwargs.get('proxy', None)
        logger.warn('Proxy: {}'.format(self.PROXY))

        self.BYPASS_CERTIFICATE_VALIDATION = kwargs.get('insecure', False)
        logger.warn('Bypassing certificate validation: {}'.format(self.BYPASS_CERTIFICATE_VALIDATION))

        self.PYTHON_DOWNLOAD_URL = 'https://www.python.org/ftp/python/2.7.12/python-2.7.12.amd64.msi'
        self.VCPYTHON27_DOWNLOAD_URL = 'https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi'

        self.DOWNLOAD_TIMEOUT = 30

    @staticmethod
    def _prepare_for_download():
        """
        Ensure everything is ready to start the download
        :return: None
        """

        logger.info('Preparing for download')

        if not os.path.exists(DOWNLOADS_DIR):
            logger.info('Creating downloads directory')
            os.makedirs(DOWNLOADS_DIR)

        logger.debug('Prepared for download')

    def download_pip_requirements(self):
        """
        Download the pip requirements
        :return: None
        """

        self._prepare_for_download()

        logger.info('Beginning download of pip requirements')

        pip_download_cmd = [
            'pip',
            'download',
            '-d', DOWNLOADS_DIR,
        ]

        if self.PROXY is not None:
            pip_download_cmd += ['--proxy', self.PROXY]

        if self.BYPASS_CERTIFICATE_VALIDATION:
            pip_download_cmd += ['--trusted-host', 'pypi.python.org']
            pip_download_cmd += ['--trusted-host', 'pypi.org']
            pip_download_cmd += ['--trusted-host', 'files.pythonhosted.org']

        # Download lxml wheels for multiple architectures
        lxml_win32 = [
            '--only-binary=:all:',
            '--platform=win32',
            '--python-version=27',
            'lxml',
        ]

        subprocess.call(
            pip_download_cmd + lxml_win32
        )

        lxml_win64 = [
            '--only-binary=:all:',
            '--platform=win_amd64',
            '--python-version=27',
            'lxml',
        ]

        subprocess.call(
            pip_download_cmd + lxml_win64
        )

        # Download all the regular dependencies
        requirements_file = ['-r', os.path.join(BASE_DIR, 'requirements.txt')]

        subprocess.call(
            pip_download_cmd + requirements_file
        )

        logger.debug('Download of pip requirements complete')

    def download_vcpython27(self):
        """
        Download vcpython27 since some Windows 7 boxes have it and some don't.
        :return: None
        """

        self._prepare_for_download()

        logger.info('Beginning download of vcpython27... this may take a few minutes...')

        with open(os.path.join(DOWNLOADS_DIR, 'vcpython27.msi'), 'wb') as f:

            if self.PROXY is not None:
                opener = urllib2.build_opener(
                    urllib2.HTTPHandler(),
                    urllib2.HTTPSHandler(),
                    urllib2.ProxyHandler({'http': self.PROXY, 'https': self.PROXY})
                )
                urllib2.install_opener(opener)

            f.write(urllib2.urlopen(self.VCPYTHON27_DOWNLOAD_URL, timeout=self.DOWNLOAD_TIMEOUT).read())

        logger.debug('Download of vcpython27 complete')

    def download_python(self):
        """
        Download Python
        :return: None
        """

        self._prepare_for_download()

        logger.info('Beginning download of python')

        with open(os.path.join(DOWNLOADS_DIR, 'python-installer.msi'), 'wb') as f:

            if self.PROXY is not None:
                opener = urllib2.build_opener(
                    urllib2.HTTPHandler(),
                    urllib2.HTTPSHandler(),
                    urllib2.ProxyHandler({'http': self.PROXY, 'https': self.PROXY})
                )
                urllib2.install_opener(opener)

            f.write(urllib2.urlopen(self.PYTHON_DOWNLOAD_URL, timeout=self.DOWNLOAD_TIMEOUT).read())

        logger.debug('Download of python complete')

parser = argparse.ArgumentParser(description='Download the requirements for an offline DART installation.')

parser.add_argument(
    '--proxy',
    type=str,
    help='proxy for https traffic',
    default=None,
)

parser.add_argument(
    '--insecure',
    action='store_true',
    help='skip certificate validation',
    default=False,
)

parser.add_argument(
    '--target',
    type=str,
    help='target operating system (changes what is downloaded)',
    choices=['w7'],
    default=None,  # None will eventually mean, just download everything just in case I need it, for now it's an alias to w7
)

args = parser.parse_args()

prepper = DartOfflinePrepper(**vars(args))

logger.info('Beginning DART offline installation preparation')

if args.target == "w7" or args.target is None:
    prepper.download_vcpython27()
    prepper.download_python()
    prepper.download_pip_requirements()

logger.info('DART offline installation preparation complete')
