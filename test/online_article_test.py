import os
import unittest
import bs4
from src import myrequests
from src import online_article

class Test(unittest.TestCase):
    pass

    def save_html_if_not_exist(self, url):
        filename = url.split("/")[-1]
        if not os.path.exists(filename):
            response = myrequests.get(url)
            with open(filename, "wb") as f:
                f.write(response.content)
        return filename

    # def test_sg_ch(self):
    #     url = "https://www.sg.ch/news/sgch_allgemein/2026/03/ein-modernes-volksschulgesetz-fuer-st-gallen-.html"
    #     filename = self.save_html_if_not_exist(url)
    #     content = open(filename).read()
    #     test_soup = bs4.BeautifulSoup(content, "html.parser")
    #     print(test_soup.prettify())
    #     article = online_article.article_from_soup(test_soup, url)
    #     for key in article.keys():
    #         print(key, article[key])

