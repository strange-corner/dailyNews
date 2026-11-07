import unittest

from src import directoryParser
from src import myrequests

testdatafile = "test/testdata/directoryParserTestdata_kapoAR.html"

class DirectoryParserTest(unittest.TestCase):

    def test_is_list(self):
        testdata = self._read_testdata()
        self.assertIsInstance(directoryParser.parse_article_directory(testdata), list)

    def test_9_articles(self):
        testdata = self._read_testdata()
        articlelist = directoryParser.parse_article_directory(testdata)
        self.assertEqual(len(articlelist), 9)

    def test_first_article_details(self):
        testdata = self._read_testdata()
        articlelist = directoryParser.parse_article_directory(testdata)
        testarticle = articlelist[0]
        self.assertEqual("Unfall zwischen Auto und Roller", testarticle["title"])
        self.assertEqual("06.11.2026", testarticle["published"])

    def _read_testdata(self):
        with open(testdatafile) as f:
            html = f.read()
            return html

    def downloadTestData(self):
        url = "https://ar.ch/verwaltung/departement-inneres-und-sicherheit/kantonspolizei/medienmitteilungen-der-kantonspolizei/"
        r = myrequests.get(url)
        with open(testdatafile, "wb") as f:
            f.write(r.content)

    # def test_download(self):
    #     self.downloadTestData()


