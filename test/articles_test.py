import unittest
import sys
import datetime
sys.path.append("src")
sys.path.append("../src")

from src.articles import filter_articles_published_after

class ArticlesTest(unittest.TestCase):

    def test_filter_by_date(self):
        articles = list([dict(), dict()])
        articles[0]["published"] = "Wed, 01 Jan 2024 00:00:00 +01:00"
        articles[1]["published"] = "Wed, 01 Jan 2026 00:00:00 +01:00"

        filterdate = datetime.datetime(2025, 1, 1)
        filtered = filter_articles_published_after(articles, filterdate)

        self.assertEqual(1, len(filtered))

        filterdate = datetime.datetime.now()
        filtered = filter_articles_published_after(articles, filterdate)

        self.assertEqual(0, len(filtered))
