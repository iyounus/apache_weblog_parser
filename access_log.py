from datetime import datetime
import requests
from requests.exceptions import Timeout, ConnectionError
import re
import collections


class AccessLog:
    # input line example
    '''
    108.182.91.188 - - [21/Oct/2014:05:36:06 -0700] "GET /svds.com/favicon.ico HTTP/1.1" 404 234 "http://svds.com/rockandroll/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.77.4 (KHTML, like Gecko) Version/7.0.5 Safari/537.77.4"
    '''

    def __init__(self):
        self.regex_pattern \
            = '^(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}) (\w+|-) ' + \
            '(\w+|-) \[(\d{2}\/[A-Za-z]{3}\/\d{4}):(\d{2}:\d{2}:\d{2}) ' + \
            '(-\d{4})\] "GET (.+) .+" (\d+) (\d+|-) "(http.*)" (.+)$'

        self.ip_dict = {}
        self.access_logs = []

        # self.db, self.collection = self.init_mongo()

    # def init_mongo(self):
    #     client = MongoClient()
    #     db = client.svds
    #     collection = db.iplookup
    #     return db, collection

    def match_pattern(self, line, log):
        '''
        INPUT string, dict
        OUTPUT none

        Extracts information from input line using regex pattern.
        Input line is expected to be a signle log entry.
        '''
        match = re.match(self.regex_pattern, line)
        if match:
            log['ip_address'] = match.group(1)
            date = match.group(4)
            time = match.group(5)
            log['epoch'] = self.to_epoch(date, time)
            # log.tz = match.group(6)
            log['uri'] = match.group(7)
            log['referrer'] = match.group(10)
        else:
            print 'Invalid log entry:', line

    def to_epoch(self, date, time):
        '''
        INPUT string, string

        converts date and time to epoch time
        Input date example: 21/Oct/2014
        Input time example: 05:36:06 (24 hour time)
        '''

        try:
            date_time = datetime.strptime(date + time, '%d/%b/%Y%H:%M:%S')
            return int(date_time.strftime('%s'))
        except ValueError:
            print 'Invalid date format or string is empty.'
            return None

    def ip_lookup(self, ip, log):
        '''
        INPUT string, dict
        OUTPUT none
        '''
        self.ip_request(ip)

        if ip in self.ip_dict:
            log['latitude'] = self.ip_dict[ip]['latitude']
            log['longitude'] = self.ip_dict[ip]['longitude']
            log['isp'] = self.ip_dict[ip]['isp']
            log['organization'] = self.ip_dict[ip]['organization']

    def ip_request(self, ip):
        '''
        INPUT string

        Takes an ip address, makes a call to ApiGurus api to obtain
        location information for ip. See docs at
        http://www.apigurus.com
        '''
        if ip not in self.ip_dict:
            url = 'http://api.apigurus.com/iplocation/v1.8/locateip?'
            url += 'key=SAKE3B7Z7HR63A6Z96ZZ'
            url += '&ip=' + ip
            url += '&format=JSON'

            try:
                r = requests.get(url)
                if r.status_code == requests.codes.ok:
                    data = r.json()['geolocation_data']

                    self.ip_dict[ip] = {}
                    self.ip_dict[ip]['latitude'] = data['latitude']
                    self.ip_dict[ip]['longitude'] = data['longitude']
                    self.ip_dict[ip]['isp'] = data['isp']
                    self.ip_dict[ip]['organization'] = data['organization']
                else:
                    print 'API request failed for ip:', ip
                    print 'Request return code:', r.status_code
            except (Timeout, ConnectionError) as e:
                print 'API request failed for ip:', ip
                print e

    def read_logs(self, file_name):
        fail = 0

        with open(file_name) as f:
            for line in f.readlines():
                log = {}
                self.match_pattern(line, log)

                # if the match_pattern fails, log will be empty
                if log:
                    self.ip_lookup(log['ip_address'], log)
                    self.access_logs.append(log)
                else:
                    fail += 1
        return fail

    def write_logs(self, file_name):
        # with open(file_name, 'w') as fout:
        #     json.dump(self.access_logs, fout)
        with open(file_name, 'w') as fout:
            for log in self.access_logs:
                log_ordered \
                    = collections.OrderedDict(sorted(log.items())).values()
                log_ordered = [str(item) for item in log_ordered]
                fout.write(','.join(log_ordered) + '\n')


if __name__ == "__main__":
    logs = AccessLog()
    n_fail = logs.read_logs('access.log')
    print 'invalid logs:', n_fail
    logs.write_logs('access.csv')
