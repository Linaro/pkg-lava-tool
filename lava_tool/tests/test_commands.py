# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
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

"""
Unit tests for the launch_control.commands package
"""

from mocker import MockerTestCase

from lava_tool.interface import (
    Command,
    LavaCommandError,
    )
from lava_tool.dispatcher import (
    LavaDispatcher,
    main,
    )


class CommandTestCase(MockerTestCase):

    def test_register_arguments_does_nothing(self):
        parser = self.mocker.mock()
        self.mocker.replay()
        Command.register_arguments(parser)

    def test_not_implemented(self):
        self.assertRaises(NotImplementedError, Command(None, None).invoke)

    def test_get_name_uses_class_name(self):
        class Foo(Command):
            pass
        self.assertEqual(Foo.get_name(), "Foo")

    def test_get_name_strips_leading_underscore(self):
        class _Bar(Command):
            pass
        self.assertEqual(_Bar.get_name(), "Bar")

    def test_get_name_converts_underscore_to_dash(self):
        class froz_bot(Command):
            pass
        self.assertEqual(froz_bot.get_name(), "froz-bot")

    def test_get_help_uses_docstring(self):
        class ASDF(Command):
            """
            This command was named after the lisp package management system
            """
        self.assertEqual(
            ASDF.get_help(),
            'This command was named after the lisp package management system')

    def test_get_help_defaults_to_None(self):
        class mysterious(Command):
            pass

        self.assertEqual(mysterious.get_help(), None)

    def test_get_epilog_defaults_to_None(self):
        class mysterious(Command):
            pass
        self.assertEqual(mysterious.get_epilog(), None)

    def test_get_epilog_returns_data_after_carriage_L(self):
        # The dot after 'before' is to make pep8 happy
        class help_with_epilog(Command):
            """
            before
            .
            after
            """
        self.assertEqual(help_with_epilog.get_epilog(), "after")

    def test_get_help_returns_data_before_carriage_L(self):
        # The dot after 'before' is to make pep8 happy
        class help_with_epilog(Command):
            """
            before
            .
            after
            """
        self.assertEqual(help_with_epilog.get_help(), "before\n.")


class DispatcherTestCase(MockerTestCase):

    def test_main(self):
        mock_LavaDispatcher = self.mocker.replace(
            'lava_tool.dispatcher.LavaDispatcher')
        mock_LavaDispatcher().dispatch()
        self.mocker.replay()
        self.assertRaises(SystemExit, main)

    def test_add_command_cls(self):
        test_calls = []

        class test(Command):

            def invoke(self):
                test_calls.append(None)

        dispatcher = LavaDispatcher()
        dispatcher.add_command_cls(test)
        dispatcher.dispatch(raw_args=['test'])
        self.assertEqual(1, len(test_calls))

    def test_print_LavaCommandError_nicely(self):
        stderr = self.mocker.replace('sys.stderr', passthrough=False)
        stderr.write("ERROR: error message")
        stderr.write("\n")
        self.mocker.replay()

        class error(Command):

            def invoke(self):
                raise LavaCommandError("error message")

        dispatcher = LavaDispatcher()
        dispatcher.add_command_cls(error)
        exit_code = dispatcher.dispatch(raw_args=['error'])
        self.assertEquals(1, exit_code)
