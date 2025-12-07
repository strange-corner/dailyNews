import re
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

    def test_char_replace(self):
        teststr = "Wir brauchen 5 % mehr"
        self.assertEqual("Wir brauchen 5 \\% mehr", article_codec._encode_special_chars(teststr))

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

