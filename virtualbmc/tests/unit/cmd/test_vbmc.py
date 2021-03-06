# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six
import sys

import mock

from virtualbmc.cmd import vbmc
from virtualbmc import manager
from virtualbmc.tests.unit import base
from virtualbmc.tests.unit import utils as test_utils


@mock.patch.object(sys, 'exit', lambda _: None)
class VBMCTestCase(base.TestCase):

    def setUp(self):
        super(VBMCTestCase, self).setUp()
        self.domain = test_utils.get_domain()

    @mock.patch.object(manager.VirtualBMCManager, 'add')
    def test_main_add(self, mock_add):
        argv = ['add']
        for option, value in self.domain.items():
            if option != 'domain_name':
                argv.append('--' + option.replace('_', '-'))
                argv.append(value and str(value))
        argv.append(self.domain['domain_name'])
        vbmc.main(argv)
        mock_add.assert_called_once_with(**self.domain)

    @mock.patch.object(manager.VirtualBMCManager, 'delete')
    def test_main_delete(self, mock_delete):
        argv = ['delete', 'foo', 'bar']
        vbmc.main(argv)
        expected_calls = [mock.call('foo'), mock.call('bar')]
        self.assertEqual(expected_calls, mock_delete.call_args_list)

    @mock.patch.object(manager.VirtualBMCManager, 'start')
    def test_main_start(self, mock_start):
        argv = ['start', 'SpongeBob']
        vbmc.main(argv)
        mock_start.assert_called_once_with('SpongeBob')

    @mock.patch.object(manager.VirtualBMCManager, 'stop')
    def test_main_stop(self, mock_stop):
        argv = ['stop', 'foo', 'bar']
        vbmc.main(argv)
        expected_calls = [mock.call('foo'), mock.call('bar')]
        self.assertEqual(expected_calls, mock_stop.call_args_list)

    @mock.patch.object(manager.VirtualBMCManager, 'list')
    def test_main_list(self, mock_list):
        argv = ['list']

        mock_list.return_value = [
            {'domain_name': 'node-1',
             'status': 'running',
             'address': '::',
             'port': 321},
            {'domain_name': 'node-0',
             'status': 'running',
             'address': '::',
             'port': 123}]

        with mock.patch.object(sys, 'stdout', six.StringIO()) as output:
            vbmc.main(argv)
            out = output.getvalue()
            expected_output = """\
+-------------+---------+---------+------+
| Domain name | Status  | Address | Port |
+-------------+---------+---------+------+
| node-0      | running | ::      |  123 |
| node-1      | running | ::      |  321 |
+-------------+---------+---------+------+
"""
            self.assertEqual(expected_output, out)

        self.assertEqual(mock_list.call_count, 1)

    @mock.patch.object(manager.VirtualBMCManager, 'show')
    def test_main_show(self, mock_show):
        argv = ['show', 'SpongeBob']

        self.domain['status'] = 'running'
        mock_show.return_value = self.domain

        with mock.patch.object(sys, 'stdout', six.StringIO()) as output:
            vbmc.main(argv)
            out = output.getvalue()
            expected_output = """\
+-----------------------+-----------+
| Property              | Value     |
+-----------------------+-----------+
| address               | ::        |
| domain_name           | SpongeBob |
| libvirt_sasl_password | None      |
| libvirt_sasl_username | None      |
| libvirt_uri           | foo://bar |
| password              | pass      |
| port                  | 123       |
| status                | running   |
| username              | admin     |
+-----------------------+-----------+
"""
            self.assertEqual(expected_output, out)

        self.assertEqual(mock_show.call_count, 1)
