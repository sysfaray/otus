import unittest
import datetime
import log_analyzer
config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./test_log", "LOGGING_DIR":  "./logs"}

class TestSum(unittest.TestCase):
    def test_config(self):
        self.assertDictEqual(log_analyzer.check_config(config), config)

    def test_gen_find(self):
        self.assertEqual(log_analyzer.gen_find(
        "nginx-access-ui.log-*", config.get("LOG_DIR"), config.get("REPORT_DIR")),
            ['./test_log/nginx-access-ui.log-20170630.gz', '2017.06.30'])

    def test_get_date(self):
        self.assertEqual(log_analyzer.get_date(['nginx-access-ui.log-20170630.gz', 'nginx-access-ui.log-20170530.gz']),
                         datetime.date(2017, 6, 30))

if __name__ == "__main__":
    unittest.main()