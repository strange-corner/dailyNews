import unittest

import feed

class FeedTest(unittest.TestCase):

    def html_from_file(self, filename):
        with open(filename, "r") as f:
            summary_html = f.read()
        return summary_html


    def summary_from_file(self, filename, expected_content_lines: int):

        parts = feed.parts_from_feed_summary(self.html_from_file((filename)))

        for part in parts:
            print(part)

        self.assertEqual(expected_content_lines, len(parts[1].splitlines()))
        print("****************************************")


    def test_all(self):
        """ Einfach mal durchlaufen lassen, und es soll nix crashen"""
        self.summary_from_file("testdata/feed_summary_testdata.txt", 72)  # Erfahrungswert
        self.summary_from_file("testdata/feed_summary_testdata2.txt", 72)