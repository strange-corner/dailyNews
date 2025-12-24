import unittest
import jotform
from datetime import datetime

TESTFILE = "jotform_textdata.txt"

class JotformText(unittest.TestCase):

    def maintenance_downlaod_testdata(self):
        """ kann einmalig manuell ausgeführt werden, um Testdaten herunterzuladen"""
        content = jotform.download_submissions()
        with open(TESTFILE, "wb") as f:
            f.write(content)

    def test_decode(self):
        with open("jotform_textdata.txt", "rb") as f:
            testdata = f.read()
        events = jotform.extract_events(testdata)
        print(events)

        text = jotform.generate_text_for_date(events, datetime.strptime("2025-12-30", "%Y-%m-%d").date())
        print(text)



