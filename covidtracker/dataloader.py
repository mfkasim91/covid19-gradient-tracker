import os
import datetime
import pandas as pd
import numpy as np
import covidtracker as ct

class DataLoader(object):
    def __init__(self, dataidentifier):
        self.address = {
            "id_new_cases": {
                "file": "data/indonesia.csv",
                "xticks": lambda pddata: pddata.tanggal,
                "retrieve_fcn": lambda pddata: pddata.kasus_baru,
                "ylabel": "Kasus positif baru per hari",
            },
            "id_new_cases_test_adjusted": {
                "file": "data/indonesia.csv",
                "xticks": lambda pddata: pddata.tanggal,
                "retrieve_fcn": adjust_new_cases_with_tests,
                "ylabel": "Kasus positif per hari (disesuaikan dengan jumlah pemeriksaan)"
            },
            "id_new_deaths": {
                "file": "data/indonesia.csv",
                "xticks": lambda pddata: pddata.tanggal,
                "retrieve_fcn": lambda pddata: pddata.meninggal_baru,
                "ylabel": "Kasus kematian baru per hari",
            },
            "id_new_tests": {
                "file": "data/indonesia.csv",
                "xticks": lambda pddata: pddata.tanggal,
                "retrieve_fcn": new_test_fcn,
                "ylabel": "Pemeriksaan per hari",
            },

            "jkt_deaths_protap": {
                "file": "data/jakarta.csv",
                "xticks": lambda pddata: pddata.tanggal[16:],
                "retrieve_fcn": lambda pddata: np.asarray(pddata.pemakaman_protap[16:]),
                "ylabel": "Pemakaman protap COVID-19",
            }
        }[dataidentifier]
        self.dataidentifier = dataidentifier
        self.ct_path = os.path.split(ct.__file__)[0]

        pddata = pd.read_csv(self.get_full_address(self.address["file"]))
        self._data = np.asarray(self.address["retrieve_fcn"](pddata))
        self._xticks = np.asarray(self.address["xticks"](pddata))

    @property
    def ytime(self):
        return self._data

    @property
    def tdate(self):
        return self._xticks

    @property
    def ylabel(self):
        return self.address["ylabel"]

    def get_full_address(self, reladdr):
        return os.path.join(self.ct_path, reladdr)

    def get_fname(self):
        today = datetime.date.today()
        fname = "%s-%s.pkl" % (today.strftime("%y%m%d"), self.dataidentifier)
        fpath = self.get_full_address(os.path.join("samples", fname))
        return fpath

def new_test_fcn(pddata):
    tests = np.asarray(pddata.jumlah_diperiksa)
    new_tests = tests[1:] - tests[:-1]
    new_tests = np.concatenate((new_tests[:1], new_tests))
    new_tests[new_tests < 0] = 50.0
    return new_tests

def adjust_new_cases_with_tests(pddata):
    new_tests = new_test_fcn(pddata)
    new_cases = pddata.kasus_baru
    pct = new_cases / new_tests
    ratio = pct / 0.1
    return new_cases * ratio