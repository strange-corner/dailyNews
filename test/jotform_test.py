import unittest
from src import jotform
from datetime import datetime
from pathlib import Path

TEST_DIR = Path(__file__).parent
TESTDATA_DIR = TEST_DIR / "testdata"

TESTFILE = (
    TESTDATA_DIR / "jotform_testdata.txt",
    TESTDATA_DIR / "jotform_textdata.txt"
)

class JotformText(unittest.TestCase):

    @staticmethod
    def maintenance_downlaod_testdata():
        """ kann einmalig manuell ausgeführt werden, um Testdaten herunterzuladen"""
        content = jotform.download_submissions()
        with open(TESTFILE[-1], "wb") as f:
            f.write(content)

    def test_decode(self):
        for tf in TESTFILE:
            with open(tf, "rb") as f:
                testdata = f.read()
            events = jotform.extract_events(testdata)
            print(events)

            text = jotform.generate_text_for_date(events, datetime.strptime("2025-12-30", "%Y-%m-%d").date())
            print(text)

    def test_item_str_from_eventDict(self):
        testevent = {'titel': 'Sauknapp Party 2026', 'ort': 'Chälblihalle Herisau', 'zeit': '15:00', 'link': 'sauknapp.ch'}
        exp_result = "Sauknapp Party 2026, Chälblihalle Herisau, 15:00, {\\urlstyle{same}\\url{sauknapp.ch} }\n"
        act_result = jotform._item_str_from_even_dict(testevent)
        self.assertEqual(act_result, exp_result)




