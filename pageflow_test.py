import unittest
from pageflow import *

class Test(unittest.TestCase):

    def test1(self):
        testee = PageFlow()
        testee.add(CategoryMarker("0"))
        testee.add(CategoryMarker("1"))
        testee.add(CategoryMarker("2"))
        testee.move_dn([0])
        self.assertEqual("1", testee.elements()[0].ident())
        self.assertEqual("0", testee.elements()[1].ident())
        self.assertEqual("2", testee.elements()[2].ident())

    def test2(self):
        testee = PageFlow()
        testee.add(CategoryMarker("0"))
        testee.add(CategoryMarker("1"))
        testee.add(CategoryMarker("2"))
        testee.move_dn([0, 1])
        self.assertEqual("2", testee.elements()[0].ident())
        self.assertEqual("0", testee.elements()[1].ident())
        self.assertEqual("1", testee.elements()[2].ident())
