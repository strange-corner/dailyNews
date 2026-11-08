import unittest
import sys
import datetime
sys.path.append("src")
sys.path.append("../src")
import util

from src import util


class UtilTest(unittest.TestCase):

    def test_filter_by_date(self):
        articles = list([dict(), dict()])
        articles[0]["published"] = "Wed, 01 Jan 2024 00:00:00 +01:00"
        articles[1]["published"] = "Wed, 01 Jan 2026 00:00:00 +01:00"

        filterdate = util.datetime_from_published_str("Wed, 01 Jan 2025 00:00:00 +01:00")
        filtered = util.filter_articles_older_than(articles, filterdate)

        self.assertEqual(1, len(filtered))

        filterdate = datetime.datetime.now()
        filtered = util.filter_articles_older_than(articles, filterdate)

        self.assertEqual(0, len(filtered))
