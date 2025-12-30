import unittest
from src.pageflow import *


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

    def test_when_article_exists_then_overwrite(self):
        testee = PageFlow()
        testee.add(Article("a_article1"))
        testee.add(Article("a_article2"))

        testee.add(Article("a_article1"))

        self.assertEqual(2, len(testee.elements()), "Anzahl bleibt stabil")
        self.assertEqual("a_article1", testee.elements()[0].ident(), "Wird an Ort und Stelle ersetzt")
