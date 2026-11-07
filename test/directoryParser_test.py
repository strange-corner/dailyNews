from datetime import datetime
import unittest

from src import directoryParser
from src import myrequests

testdatafile = "test/testdata/directoryParserTestdata_HerisauCh.html"

class DirectoryParserTest(unittest.TestCase):

    def test_is_list(self):
        testdata = self._read_testdata()
        self.assertIsInstance(directoryParser.parse_article_directory(testdata), list)

    def test_9_articles(self):
        testdata = self._read_testdata("test/testdata/directoryParserTestdata_kapoAR.html")
        articlelist = directoryParser.parse_article_directory(testdata)
        self.assertEqual(len(articlelist), 9)

    def test_251_articles_herisauCh(self):
        testdata = self._read_testdata()
        articlelist = directoryParser.parse_article_directory(testdata)
        self.assertEqual(251, len(articlelist))

    def test_first_article_details(self):
        testdata = self._read_testdata("test/testdata/directoryParserTestdata_kapoAR.html")
        articlelist = directoryParser.parse_article_directory(testdata)
        testarticle = articlelist[0]
        self.assertEqual("Unfall zwischen Auto und Roller", testarticle["title"])
        self.assertEqual("06.11.2026", testarticle["published"])

    def test_first_article_details_herisau_ch(self):
        testdata = self._read_testdata()
        articlelist = directoryParser.parse_article_directory(testdata)
        testarticle = articlelist[0]
        self.assertEqual("Ja zu Bahnhof-Vorlagen sorgt für Erleichterung", testarticle["title"])
        self.assertEqual("27.09.2020", testarticle["published"])

    def test_filter_by_date(self):
        testdata = self._read_testdata()
        articlelist = directoryParser.parse_article_directory(testdata)
        testdate = datetime.strptime("2026-11-03", "%Y-%m-%d")
        filtered_list = directoryParser.filter_articles_published_after(articlelist, testdate)
        self.assertEqual(len(filtered_list), 3)

    def _read_testdata(self, filename=testdatafile):
        with open(filename) as f:
            html = f.read()
            return html

    def downloadTestData(self):
        url = "https://www.herisau.ch/aktuellesinformationen"
        r = myrequests.get(url)
        with open(testdatafile, "wb") as f:
            f.write(r.content)

    # def test_download(self):
    #     self.downloadTestData()


