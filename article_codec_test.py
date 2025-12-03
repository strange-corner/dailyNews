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
        self.teiltest()

    def test_encode_decode_mit_bild(self):
        self.article['image'] = "https://ar.ch/fileadmin/_processed_/d/3/csm_2025_12_01_Brand_Wienacht-Tobel__dma__ddd463a848.jpg"
        self.teiltest()

    def teiltest(self):
        article_codec.encode(self.filepath, self.article)
        read_article = article_codec.decode(self.filepath)
        for key, value in read_article.items():
            self.assertEqual(value, self.article[key], f"{key} must match")

    def test_char_replace(self):
        teststr = "Wir brauchen 5 % mehr"
        self.assertEqual("Wir brauchen 5 \\% mehr", article_codec._encode_special_chars(teststr))


