from datetime import datetime
import unittest
import sys
sys.path.append("src")
import web_directoryParser
import myrequests
import articles

testdatafile = "test/testdata/directoryParserTestdata_HerisauCh.html"

class DirectoryParserTest(unittest.TestCase):

    def test_is_list(self):
        testdata = self._read_testdata()
        self.assertIsInstance(web_directoryParser.parse_article_directory(testdata), list)

    def test_article_count_parametrized(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", 9),
            (testdatafile, 251),
        ]
        for filename, expected in cases:
            with self.subTest(filename=filename, expected=expected):
                testdata = self._read_testdata(filename)
                articlelist = web_directoryParser.parse_article_directory(testdata)
                self.assertEqual(expected, len(articlelist))

    def test_first_article_details_parametrized(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", "Unfall zwischen Auto und Roller", "06.11.2026"),
            (testdatafile, "Ja zu Bahnhof-Vorlagen sorgt für Erleichterung", "27.09.2020"),
        ]
        for filename, exp_title, exp_published in cases:
            with self.subTest(filename=filename):
                testdata = self._read_testdata(filename)
                articlelist = web_directoryParser.parse_article_directory(testdata)
                testarticle = articlelist[0]
                self.assertEqual(exp_title, testarticle["title"])
                self.assertEqual(exp_published, testarticle["published"])

    def test_filter_by_date(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", 3),
            (testdatafile, 8),
        ]
        for filename, exp_count in cases:
            testdata = self._read_testdata(filename)
            articlelist = web_directoryParser.parse_article_directory(testdata)
            testdate = datetime.strptime("2026-11-03", "%Y-%m-%d")
            filtered_list = articles.filter_articles_published_after(articlelist, testdate)
            self.assertEqual(exp_count, len(filtered_list))

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


