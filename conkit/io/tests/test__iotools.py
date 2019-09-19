"""Testing facility for conkit.io._iotools"""

__author__ = "Felix Simkovic"
__date__ = "21 Nov 2016"

import os
import unittest

from conkit.io import _iotools
from conkit.io.tests.helpers import ParserTestCase


class Test(ParserTestCase):

    def test_create_tmp_f_1(self):
        fname = self._create_iotools_fname()
        self.assertTrue(os.path.isfile(fname))

    def test_create_tmp_f_2(self):
        content = "Hello, World!"
        fname = self._create_iotools_fname(content=content, mode="w")
        self.assertTrue(os.path.isfile(fname))
        with open(fname, "r") as f_in:
            written_content = f_in.read()
        self.assertEqual(content, written_content)

    def test_create_tmp_f_3(self):
        content = b"Hello, World!"
        fname = self._create_iotools_fname(content=content, mode="wb")
        self.assertTrue(os.path.isfile(fname))
        with open(fname, "rb") as f_in:
            written_content = f_in.read().decode('utf-8')
        self.assertEqual(content, written_content)

    def test_is_str_like_1(self):
        self.assertTrue(_iotools.is_str_like("foo"))  # str
        self.assertFalse(_iotools.is_str_like(1))  # int
        self.assertFalse(_iotools.is_str_like(1.0))  # float
        self.assertFalse(_iotools.is_str_like([]))  # list
        self.assertFalse(_iotools.is_str_like(()))  # tuple
        self.assertFalse(_iotools.is_str_like({}))  # dict
        self.assertFalse(_iotools.is_str_like(set()))  # set

    def test_open_f_handle_1(self):
        fname = self._create_iotools_fname()
        with _iotools.open_f_handle(fname, "append") as fhandle:
            self.assertEqual("a", fhandle.mode)
        f_in_handle = _iotools.open_f_handle(fname, "append")
        with _iotools.open_f_handle(f_in_handle, "append") as fhandle:
            self.assertEqual("a", fhandle.mode)
        f_in_handle.close()

    def test_open_f_handle_2(self):
        fname = self._create_iotools_fname()
        with _iotools.open_f_handle(fname, "read") as fhandle:
            self.assertEqual("r", fhandle.mode)
        f_in_handle = _iotools.open_f_handle(fname, "read")
        with _iotools.open_f_handle(f_in_handle, "read") as fhandle:
            self.assertEqual("r", fhandle.mode)
        f_in_handle.close()

    def test_open_f_handle_3(self):
        fname = self._create_iotools_fname()
        with _iotools.open_f_handle(fname, "write") as fhandle:
            self.assertEqual("w", fhandle.mode)
        f_in_handle = _iotools.open_f_handle(fname, "write")
        with _iotools.open_f_handle(f_in_handle, "write") as fhandle:
            self.assertEqual("w", fhandle.mode)
        f_in_handle.close()

    def test_open_f_handle_4(self):
        fname = self._create_iotools_fname()
        with _iotools.open_f_handle(fname, "write") as fhandle:
            self.assertEqual("w", fhandle.mode)
            fhandle.write("hello world!")
        with _iotools.open_f_handle(fname, "read") as fhandle:
            self.assertEqual("r", fhandle.mode)
            self.assertEqual("hello world!", fhandle.read().strip())

    def test_open_f_handle_5(self):
        with self.assertRaises(TypeError):
            _iotools.open_f_handle(1, "read")
        with self.assertRaises(TypeError):
            _iotools.open_f_handle(1.0, "write")

    def test_open_f_handle_6(self):
        fname = self._create_iotools_fname()
        with self.assertRaises(ValueError):
            _iotools.open_f_handle(fname, "foo")
        with self.assertRaises(ValueError):
            _iotools.open_f_handle(fname, "bar")


if __name__ == "__main__":
    unittest.main(verbosity=2)
