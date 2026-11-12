import unittest
import sys

import feedparser

sys.path.append("..")
from src import feed, myrequests
from pathlib import Path

TEST_DIR = Path(__file__).parent
TESTDATA_DIR = TEST_DIR / "testdata"


def download_test_data(url):
    data = myrequests.get(url).content
    with open(TESTDATA_DIR / "feed_summary_admin_ch.txt", "wb") as f:
        f.write(data)


class FeedTest(unittest.TestCase):

    def html_from_file(self, filename)-> str:
        with open(filename, "r", encoding='latin-1') as f:
            summary_html = f.read()
        return summary_html


    def summary_from_file(self, filename, expected_content_lines: int):

        parts = feed._parts_from_feed_summary(self.html_from_file((filename)))

        for part in parts:
            print(part)

        self.assertEqual(expected_content_lines, len(parts[1].splitlines()))
        print("****************************************")


    def test_all(self):
        """ Einfach mal durchlaufen lassen, und es soll nix crashen"""
        self.summary_from_file(TESTDATA_DIR / "feed_summary_testdata.txt", 72)  # Erfahrungswert
        self.summary_from_file(TESTDATA_DIR / "feed_summary_testdata2.txt", 72)
        self.summary_from_file(TESTDATA_DIR / "feed_a_Kanton_St29.txt", 38)

    def test_admin_ch_directory(self):
        with open(TESTDATA_DIR / "feed_summary_admin_ch.txt", "rb") as f:
            feedo = feedparser.parse(f)
        articles = feed.articles_from_feed_entries(feedo, {"url": "https://www.newsd.admin.ch/newsd/en/home.html",
                                                                  "quelle": "News Service Bund"})
        self.assertEqual(499, len(articles))
        print(articles)

if __name__ == '__main__':
    download_test_data("https://www.newsd.admin.ch/newsd/feeds/rss?lang=de&org-nr=1")