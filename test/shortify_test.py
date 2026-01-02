import unittest

from src import shortify


class ShortifyTest(unittest.TestCase):

    def test_get_chached_slug(self):
        TESTURL = "https://schweizerzeit.ch/der-fall-jacques-baud-hoffentlich-ein-augenoeffner/"
        EXP_SLUG = "bts8"
        slug = shortify.get_slug_from_db(TESTURL)
        self.assertEqual(slug, EXP_SLUG)  # add assertion here


    def test_get_chached_slug_when_shortlink_is_passed(self):
        """ Wenn ein Artikel erneut gespeichert wird, und bereits der shortlink übergeben wird, soll das erkannt und dieser
        zurückgegeben werden. """
        TESTURL = "https://gbsn.ch/bts8"
        EXP_SLUG = "bts8"
        slug = shortify.get_slug_from_db(TESTURL)
        self.assertEqual(slug, EXP_SLUG)  # add assertion here


