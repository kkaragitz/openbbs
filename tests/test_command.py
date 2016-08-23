import unittest

from openbbs.command import CommandInterpreter


class CommandInterpereterTest(unittest.TestCase):
    def test_resolve_default_function(self):
        command_interpreter = CommandInterpreter(lambda _, x: x, ("Foo!",), ())
        self.assertEqual(command_interpreter.call(("bar",)), "Foo!")

    def test_add_argument(self):
        command_interpreter = CommandInterpreter(lambda _: None, (), ())
        command_interpreter.add(("a",), lambda _, x: x, ("Foo!",))
        self.assertEqual(command_interpreter.call(("a",)), "Foo!")

    def test_utilize_base_arguments(self):
        command_interpreter = CommandInterpreter(lambda x, _: None, (), ("f",))
        command_interpreter.add(("a",), lambda x, _: x, ())
        self.assertEqual(command_interpreter.call(("a",)), "f")

    def test_throw_type_errors(self):
        command_interpreter = CommandInterpreter(lambda _: None, (), ())
        with self.assertRaises(TypeError):
            command_interpreter.add(1, lambda _: None, ())
        with self.assertRaises(TypeError):
            command_interpreter.add(("a",), 1, ())
        with self.assertRaises(TypeError):
            command_interpreter.add(("a",), lambda _: None, 1)
