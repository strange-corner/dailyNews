import re
import unittest
import article_saveload

class ArticleTest(unittest.TestCase):

    filepath = "testfile.txt"

    def setUp(self):
        self.article = {"title": "Article Title",
                        "lead": "Lead-Text, bzw. Vorspann",
                        "content": "Blah, blah blah",
                        "url": "https://news.ycombinator.com/",
                        "quelle": "Kapo AR"}

    def test_encode_decode(self):
        self.teiltest()

    def test_encode_decode_mit_bild(self):
        self.article['image'] = "https://ar.ch/fileadmin/_processed_/d/3/csm_2025_12_01_Brand_Wienacht-Tobel__dma__ddd463a848.jpg"
        self.teiltest()

    def teiltest(self):
        article_saveload.article_save(self.filepath, self.article)
        read_article = article_saveload.article_load(self.filepath)
        self.assertEqual(self.article, read_article)
        for key, value in read_article.items():
            self.assertEqual(value, self.article[key], f"{key} must match")

    def isValidFilename(self, filename) -> bool:
        ## Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*] '
        if re.search(invalid_chars, filename):
            return False
        return True


