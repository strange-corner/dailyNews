import unittest
from datetime import datetime
from src import wetterdaten

class Test(unittest.TestCase):

    testdatafile = "../test/testdata/vnut12.lssw.202603040000.tre200h0.csv"

    def test1(self):
        data = wetterdaten.get_val_of_date(self.testdatafile, datetime(2026, 3, 4))
        print(data)
        resultdict = dict()
        resultdict["id_temp_hourly_mean"] = data
        tagedict = dict()
        tagedict["heute"] = resultdict

        min, max = wetterdaten.getMinMaxTemp(tagedict)
        print(min, max)
