import re
import unittest
from src import article_codec


class ArticleTest(unittest.TestCase):

    filepath = "../testfile.txt"

    def setUp(self):
        self.article = {"title": "Article Title",
                        "lead": "Lead-Text, bzw. Vorspann",
                        "content": "Blah, blah blah",
                        "url": "https://news.ycombinator.com/",
                        "quellenArt": "Quelle",
                        "quelle": "Kapo AR"}

    def test_char_replace(self):
        teststr = "Wir brauchen 5 % mehr"
        self.assertEqual("Wir brauchen 5 \\% mehr", article_codec._encode_special_chars(teststr))

    def test_char_ampersand_replace(self):
        teststr = "Chonsch zum C&A?"
        self.assertEqual("Chonsch zum C\\&A?", article_codec._encode_special_chars(teststr))

    def test_char_underscore_replace(self):
        """ Underscore ist ein Sonderzeichen für den Mathe-Modus. """
        teststr = "Underscore_undWeiter"
        self.assertEqual("Underscore\\_undWeiter", article_codec._encode_special_chars(teststr))

    def test_char_u2005_replace(self):
        teststr = "CHF 10 000.00"
        self.assertEqual("CHF 10 000.00", article_codec._encode_special_chars(teststr))

    def isValidFilename(self, filename) -> bool:
        ## Check for invalid characters
        invalid_chars = r'[<>:"/\\|?*] '
        if re.search(invalid_chars, filename):
            return False
        return True

    def test_FilnameFromTitle(self):
        def testName(name):
            self.assertTrue(self.isValidFilename(article_codec.articleFilenameFromTitle(name)))
        testName("Motion \"Schule")

    def test_encode(self):
        mock = WriterMock()
        article_codec.encode("filepath_for_qr", self.article, mock)
        self.assertTrue(mock.output.strip().endswith("\\\\"))

class WriterMock:

    def __init__(self):
        self.output = ""

    def write(self, text):
        self.output += (text)