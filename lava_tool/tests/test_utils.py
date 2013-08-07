# Copyright (C) 2013 Linaro Limited
#
# Author: Milo Casagrande <milo.casagrande@linaro.org>
#
# This file is part of lava-tool.
#
# lava-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-tool.  If not, see <http://www.gnu.org/licenses/>.

"""lava_tool.utils tests."""

import os
import shutil
import subprocess
import sys
import tempfile

from unittest import TestCase
from mock import (
    MagicMock,
    call,
    patch,
)

from lava.tool.errors import CommandError
from lava_tool.utils import (
    can_edit_file,
    create_dir,
    edit_file,
    execute,
    has_command,
    retrieve_file,
    verify_and_create_url,
    verify_file_extension,
)


class UtilTests(TestCase):

    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = open("/dev/null", "w")
        self.original_stderr = sys.stderr
        sys.stderr = open("/dev/null", "w")
        self.original_stdin = sys.stdin
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        sys.stdin = self.original_stdin
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        os.unlink(self.temp_file.name)

    @patch("lava_tool.utils.subprocess.check_call")
    def test_has_command_0(self, mocked_check_call):
        # Make sure we raise an exception when the subprocess is called.
        mocked_check_call.side_effect = subprocess.CalledProcessError(0, "")
        self.assertFalse(has_command(""))

    @patch("lava_tool.utils.subprocess.check_call")
    def test_has_command_1(self, mocked_check_call):
        # Check that a "command" exists. The call to subprocess is mocked.
        mocked_check_call.return_value = 0
        self.assertTrue(has_command(""))

    def test_verify_file_extension_with_extension(self):
        extension = ".test"
        supported = [extension[1:]]
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=extension,
                                                    delete=False)
            obtained = verify_file_extension(
                temp_file.name, extension[1:], supported)
            self.assertEquals(temp_file.name, obtained)
        finally:
            if os.path.isfile(temp_file.name):
                os.unlink(temp_file.name)

    def test_verify_file_extension_without_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = verify_file_extension("/tmp/a_fake", extension, supported)
        self.assertEquals(expected, obtained)

    def test_verify_file_extension_with_unsupported_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = verify_file_extension(
            "/tmp/a_fake.extension", extension, supported)
        self.assertEquals(expected, obtained)

    @patch("os.listdir")
    def test_retrieve_job_file_0(self, mocked_os_listdir):
        # Make sure that exception is raised if we go through all the elements
        # returned by os.listdir().
        mocked_os_listdir.return_value = ["a_file"]
        self.assertRaises(CommandError, retrieve_file,
                          "a_path", ["ext"])

    @patch("os.listdir")
    def test_retrieve_job_file_1(self, mocked_os_listdir):
        # Pass some files and directories to retrieve_file(), and make
        # sure a file with .json suffix is returned.
        # Pass also a hidden file.
        try:
            json_file = tempfile.NamedTemporaryFile(suffix=".json")
            json_file_name = os.path.basename(json_file.name)

            file_name_no_suffix = tempfile.NamedTemporaryFile(delete=False)
            file_name_with_suffix = tempfile.NamedTemporaryFile(
                suffix=".bork", delete=False)

            temp_dir_name = "submit_command_test_tmp_dir"
            temp_dir_path = os.path.join(tempfile.gettempdir(), temp_dir_name)
            os.makedirs(temp_dir_path)

            hidden_file = tempfile.NamedTemporaryFile(
                prefix=".tmp", delete=False)

            mocked_os_listdir.return_value = [
                temp_dir_name, file_name_no_suffix.name,
                file_name_with_suffix.name, json_file_name, hidden_file.name]

            obtained = retrieve_file(tempfile.gettempdir(), ["json"])
            self.assertEqual(json_file.name, obtained)
        finally:
            os.removedirs(temp_dir_path)
            os.unlink(file_name_no_suffix.name)
            os.unlink(file_name_with_suffix.name)
            os.unlink(hidden_file.name)

    def test_retrieve_job_file_2(self):
        # Pass a file with the valid extension.
        temp_file = tempfile.NamedTemporaryFile(suffix=".json")
        obtained = retrieve_file(temp_file.name, ["json"])
        self.assertEquals(temp_file.name, obtained)

    def test_retrieve_job_file_3(self):
        # Pass a file with a non-valid extension.
        temp_file = tempfile.NamedTemporaryFile(suffix=".bork")
        self.assertRaises(
            CommandError, retrieve_file, temp_file.name, ["json"])

    @patch("os.listdir")
    def test_retrieve_job_file_4(self, mocked_os_listdir):
        # Pass hidden and wrong files and make sure exception is thrown.
        a_hidden_file = ".a_hidden.json"
        b_hidden_file = ".b_hidden.json"
        c_wrong_file = "a_wrong_file.bork"

        mocked_os_listdir.return_value = [a_hidden_file, b_hidden_file, c_wrong_file]
        self.assertRaises(
            CommandError, retrieve_file, tempfile.gettempdir(), ["json"])

    @patch("lava_tool.utils.subprocess")
    def test_execute_0(self, mocked_subprocess):
        mocked_subprocess.check_call = MagicMock()
        execute("foo")
        self.assertEqual(mocked_subprocess.check_call.call_args_list,
                         [call(["foo"])])
        self.assertTrue(mocked_subprocess.check_call.called)

    @patch("lava_tool.utils.subprocess.check_call")
    def test_execute_1(self, mocked_check_call):
        mocked_check_call.side_effect = subprocess.CalledProcessError(1, "foo")
        self.assertRaises(CommandError, execute, ["foo"])

    @patch("lava_tool.utils.subprocess")
    @patch("lava_tool.utils.has_command", return_value=False)
    @patch("lava_tool.utils.os.environ.get", return_value=None)
    @patch("lava_tool.utils.sys.exit")
    def test_edit_file_0(self, mocked_sys_exit, mocked_env_get,
                         mocked_has_command, mocked_subprocess):
        edit_file(self.temp_file.name)
        self.assertTrue(mocked_sys_exit.called)

    @patch("lava_tool.utils.subprocess")
    @patch("lava_tool.utils.has_command", side_effect=[True, False])
    @patch("lava_tool.utils.os.environ.get", return_value=None)
    def test_edit_file_1(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        edit_file(self.temp_file.name)
        expected = [call(["sensible-editor", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava_tool.utils.subprocess")
    @patch("lava_tool.utils.has_command", side_effect=[False, True])
    @patch("lava_tool.utils.os.environ.get", return_value=None)
    def test_edit_file_2(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        edit_file(self.temp_file.name)
        expected = [call(["xdg-open", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava_tool.utils.subprocess")
    @patch("lava_tool.utils.has_command", return_value=False)
    @patch("lava_tool.utils.os.environ.get", return_value="vim")
    def test_edit_file_3(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        edit_file(self.temp_file.name)
        expected = [call(["vim", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava_tool.utils.subprocess")
    @patch("lava_tool.utils.has_command", return_value=False)
    @patch("lava_tool.utils.os.environ.get", return_value="vim")
    def test_edit_file_4(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        mocked_subprocess.Popen.side_effect = Exception()
        self.assertRaises(CommandError, edit_file, self.temp_file.name)

    def test_can_edit_file(self):
        # Tests the can_edit_file method of the config command.
        # This is to make sure the device config file is not erased when
        # checking if it is possible to open it.
        expected = ("hostname = a_fake_panda02\nconnection_command = \n"
                    "device_type = panda\n")

        with open(self.temp_file.name, "w") as f:
            f.write(expected)

        self.assertTrue(can_edit_file(self.temp_file.name))
        obtained = ""
        with open(self.temp_file.name) as f:
            obtained = f.read()

        self.assertEqual(expected, obtained)

    def test_verify_and_create_url_0(self):
        expected = "https://www.example.org/"
        obtained = verify_and_create_url("www.example.org")
        self.assertEquals(expected, obtained)

    def test_verify_and_create_url_1(self):
        expected = "http://www.example.org/"
        obtained = verify_and_create_url("http://www.example.org")
        self.assertEquals(expected, obtained)

    def test_verify_and_create_url_2(self):
        expected = "http://www.example.org/RPC/"
        obtained = verify_and_create_url("http://www.example.org/RPC")
        self.assertEquals(expected, obtained)

    def test_verify_and_create_url_3(self):
        expected = "https://www.example.org/RPC/"
        obtained = verify_and_create_url("www.example.org/RPC")
        self.assertEquals(expected, obtained)

    def test_create_dir_0(self):
        try:
            temp_dir = os.path.join(tempfile.gettempdir(), "a_dir")
            create_dir(temp_dir)
            self.assertTrue(os.path.isdir(temp_dir))
        finally:
            shutil.rmtree(temp_dir)

    def test_create_dir_1(self):
        try:
            temp_dir = os.path.join(tempfile.gettempdir(), "a_dir")
            create_dir(temp_dir, "subdir")
            self.assertTrue(os.path.isdir(os.path.join(temp_dir, "subdir")))
        finally:
            shutil.rmtree(temp_dir)

    def test_create_dir_2(self):
        temp_dir = os.path.join("/", "a_temp_dir")
        self.assertRaises(CommandError, create_dir, temp_dir)
