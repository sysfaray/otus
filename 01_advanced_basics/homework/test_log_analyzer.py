import unittest
import datetime
import log_analyzer
config = {"REPORT_SIZE": 1000, "REPORT_DIR": None, "LOG_DIR": "./log", "LOGGING_DIR":  "./logs"}

class TestSum(unittest.TestCase):
    def test_config(self):
        self.assertDictEqual(log_analyzer.check_config(config), config)

    def test_get_date(self):
        self.assertEqual(log_analyzer.get_date(['nginx-access-ui.log-20170630.gz', 'nginx-access-ui.log-20170530.gz']), datetime.date(2017, 6, 30))


if __name__ == "__main__":
    unittest.main()