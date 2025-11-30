import unittest
import article_codec

class ArticleTest(unittest.TestCase):

    filepath = "testfile.txt"

    def setUp(self):
        self.article = {"title": "Article Title",
                        "lead": "Lead-Text, bzw. Vorspann",
                        "content": "Blah, blah blah",
                        "url": "https://news.ycombinator.com/",
                        "quelle": "Kapo AR"}

    def test_encode_decode(self):
        article_codec.encode(self.filepath, self.article)
        read_article = article_codec.decode(self.filepath)
        for key, value in read_article.items():
            self.assertEqual(value, self.article[key], f"{key} must match")

