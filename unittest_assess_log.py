from access_log import AccessLog
import unittest


class TestAccessLog(unittest.TestCase):

    def test_regex(self):
        log = '108.182.91.188 - - [21/Oct/2014:05:36:06 -0700] "GET /svds.com/favicon.ico HTTP/1.1" 404 234 "http://svds.com/rockandroll/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4"'

        self.assertRegexpMatches(log, AccessLog().regex_pattern)

    def test_regex_fail(self):
        invalid_log = '184.73.72.163 - - [21/Oct/2014:23:19:20 -0700] "GET /svds.com/rockandroll HTTP/1.0" 301 239 "-" "CCBot/2.0 (http://commoncrawl.org/faq/)"'
        self.assertNotRegexpMatches(invalid_log, AccessLog().regex_pattern)

    def test_to_epoch(self):
        date = '21/Oct/2014'
        time = '05:36:06'
        epoch = 1413894966
        self.assertEqual(AccessLog().to_epoch(date, time), epoch)

    def test_match_patter(self):
        line = '108.182.91.188 - - [21/Oct/2014:05:36:06 -0700] "GET /svds.com/favicon.ico HTTP/1.1" 404 234 "http://svds.com/rockandroll/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4"'

        log = {}
        AccessLog().match_pattern(line, log)
        self.assertDictEqual(log, {'epoch': 1413894966,
                                   'ip_address': '108.182.91.188',
                                   'referrer': 'http://svds.com/rockandroll/',
                                   'uri': '/svds.com/favicon.ico'})


if __name__ == '__main__':
    unittest.main()
