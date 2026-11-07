import os
import unittest
import bs4
import sys
sys.path.append("../src")
sys.path.append("src")
import myrequests
import online_article

class Test(unittest.TestCase):
    pass

    def save_html_if_not_exist(self, url):
        filename = url.split("/")[-1]
        if filename == "":
            filename = url.split("/")[-2]
        if not os.path.exists(filename):
            response = myrequests.get(url)
            with open(filename, "wb") as f:
                f.write(response.content)
        return filename

    def teiltest(self, url, parser):
        filename = self.save_html_if_not_exist(url)
        content = open(filename).read()
        test_soup = bs4.BeautifulSoup(content, "html.parser")
        print(test_soup.prettify())
        article = parser(test_soup, url)
        for key in article.keys():
            print(key, article[key])
        return article

    def test_Herisau_ch(self):
        url = "https://www.herisau.ch/aktuellesinformationen/3042187"
        url = "https://www.herisau.ch/aktuellesinformationen/3033478"
        self.teiltest(url, online_article.article_from_soup)

    # def test_sg_ch(self):
    #     url = "https://www.sg.ch/news/sgch_allgemein/2026/03/ein-modernes-volksschulgesetz-fuer-st-gallen-.html"
    #     self.teiltest(url, online_article.article_from_soup)
    #
    # def test_svp_ch(self):
    #     url = "https://www.svp.ch/aktuell/publikationen/medienmitteilungen/zuwanderung-ausser-rand-und-band-und-wir-sollen-dafuer-auch-noch-bezahlen-jetzt-zuwanderung-bremsen"
    #     self.teiltest(url, online_article.article_from_soup)

    # def test_kapo_ar(self):
    #     url = "https://ar.ch/verwaltung/departement-inneres-und-sicherheit/kantonspolizei/medienmitteilungen-der-kantonspolizei/detail/news/juengstes-teammitglied-der-kapo-ar/"
    #     article = self.teiltest(url, online_article.article_from_soup)
    #     self.assertEqual(article['quelle'], "Kapo AR")
    #     url = "https://ar.ch/schnellzugriff/medienmitteilungen-der-kantonalen-verwaltung/detail/news/engere-zusammenarbeit-der-kantone-bei-der-gemeinsamen-vermarktung-des-tourismus-appenzellerland/"
    #     article = self.teiltest(url, online_article.article_from_soup)
    #     self.assertEqual(article['quelle'], "Kanton AR")
