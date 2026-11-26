from datetime import datetime
import unittest
import sys
sys.path.append("src")
import web_directoryParser
import myrequests
import articles

#testdatafile = "test/testdata/directoryParserTestdata_HerisauCh.html"

class DirectoryParserTest(unittest.TestCase):

    def test_is_list(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html"),
            ("test/testdata/directoryParserTestdata_HerisauCh.html"),
            ("test/testdata/ar_kant_verwaltung.html")
        ]
        for filename in cases:
            testdata = self._read_testdata(filename)
            self.assertIsInstance(web_directoryParser.parse_article_directory(testdata), list)

    def test_article_count_parametrized(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", 9),
            ("test/testdata/directoryParserTestdata_HerisauCh.html", 244),
            ("test/testdata/ar_kant_verwaltung.html", 10)
        ]
        for filename, expected in cases:
            testdata = self._read_testdata(filename)
            articlelist = web_directoryParser.parse_article_directory(testdata)
            self.assertEqual(expected, len(articlelist))

    def test_first_article_details_parametrized(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", "Unfall zwischen Auto und Roller", "06.11.2026"),
            ("test/testdata/directoryParserTestdata_HerisauCh.html", "Ja zu Bahnhof-Vorlagen sorgt für Erleichterung", "27.09.2020"),
            ("test/testdata/ar_kant_verwaltung.html", f"Kantonales Tiefbauamt erhÃ¤lt ersten vollelektrischen Lieferwagen", "24.11.2026"),
        ]
        for filename, exp_title, exp_published in cases:
            testdata = self._read_testdata(filename)
            articlelist = web_directoryParser.parse_article_directory(testdata)
            testarticle = articlelist[0]
            self.assertEqual(exp_title, testarticle["title"])
            self.assertEqual(exp_published, testarticle["published"])

    def test_filter_by_date(self):
        cases = [
            ("test/testdata/directoryParserTestdata_kapoAR.html", 3, "2026-11-03"),
            ("test/testdata/directoryParserTestdata_HerisauCh.html", 7, "2026-11-03"),  # Bauplanauflage gefiltert
            ("test/testdata/ar_kant_verwaltung.html", 2, "2026-11-23"),
        ]
        for filename, exp_count, filterdatestr in cases:
            testdata = self._read_testdata(filename)
            articlelist = web_directoryParser.parse_article_directory(testdata)
            testdate = datetime.strptime(filterdatestr, "%Y-%m-%d")
            filtered_list = articles.filter_articles_published_after(articlelist, testdate)
            self.assertEqual(exp_count, len(filtered_list))

    def _read_testdata(self, filename):
        with open(filename) as f:
            html = f.read()
            return html

    def downloadTestData(self, url, filename):
        r = myrequests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)

    def test_download(self):
        # self.downloadTestData("https://www.herisau.ch/aktuellesinformationen")
        # self.downloadTestData("https://ar.ch/schnellzugriff/medienmitteilungen-der-kantonalen-verwaltung/", "ar_kant_verwaltung.html")
        pass

