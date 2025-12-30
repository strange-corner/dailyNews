import unittest

from src import feed
from pathlib import Path

TEST_DIR = Path(__file__).parent
TESTDATA_DIR = TEST_DIR / "testdata"

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