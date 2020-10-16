
#!/usr/bin/env python

import splunklib.client as client
import sys
import os
import requests
import argparse
import urllib2
import json
import re
import shutil
import csv
import json
from datetime import datetime

'''
#
#  Author      :: Robert Church ( robertchurch@robertchurch.us )
#              ::
#  Description :: The purpose of this script is to make an API call into Service Now and retrieve
#              :: in CSV format.  Script saves the report in lookups, and sends output to
#              :: STDOUT which Splunk then ingests via props.conf stanza.
#              ::
#  Usage       ::  inputs.conf
#              ::  [script://./bin/get_cmdb_report.py REPORTHASH]
#              ::  sourcetype = get_cmdb_report
#              ::  source = get_cmdb_report
#              ::  passAuth = admin
#              ::  interval = 15 0 * * *
#              ::  index = servicenow_reports
#              ::  disabled = 0
#              ::  
#              ::  props.conf
#              ::  [get_cmdb_report]
#              ::  DATETIME_CONFIG = CURRENT
#              ::  INDEXED_EXTRACTIONS = csv
#              ::  KV_MODE = none
#              ::  SHOULD_LINEMERGE = false
#              ::  disabled = false
#              ::
#  Exit Codes  ::
#              :: Exit 0 = Script successfully downloaded CSV
#              :: Exit 1 = Fatal error encountered
#              ::
'''

def get_session_key():

    session_key = sys.stdin.readline()
    m = re.search("authToken>(.+)</authToken", session_key)
    if m:
        session_key = m.group(1)
    else:
        session_key = session_key.replace("sessionKey=", "").strip()
    if (session_key):
        log("Obtained session key")
        session_key = urllib2.unquote(session_key.encode("ascii"))
        session_key = session_key.decode("utf-8")
        return session_key
    else:
        log("FATAL :: No session key returned")
        exit(1)

def log(msg):
    '''
        INPUT   msg     STRING          Represents data to be written to the log
    '''
    log_path='/opt/splunk/var/log/splunk/TA_servicenow-reports.log'

    f = open(os.path.realpath(log_path), "a")
    print >> f, str(datetime.now().isoformat()), msg
    f.close()

def get_CSV(API_URL, USER, PASS, local_filename):
    proxy = {'https': 'http://proxyhost:80'}
    response = requests.get(API_URL, stream=True, auth=requests.auth.HTTPBasicAuth(USER, PASS), verify=False, proxies=proxy)
    log("Downloading report to %s" % local_filename)

    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
    else:
        log("FATAL :: Unable to establish connection with API server.")
        sys.exit(1)

def get_credentials(username):
    try:
        password=''
        session_key = get_session_key()
        splunkService = client.connect(token=session_key)
        storage_passwords = splunkService.storage_passwords
        if (storage_passwords):
            log("Storage object obtained")
            for credential in storage_passwords:
                if (credential.content.get('username') == username):
                    log("API User extracted")
                    password=credential.content.get('clear_password')

            if (password):
                creds=[username,password]
                return creds
        else:
            log("No storage_passwords object")
    except Exception as error:
        log("Encountered error :: %s " % error)

def print_file(CSV_REPORT_NAME):

    try:
        with open(CSV_REPORT_NAME, 'rb') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                event_time = datetime.now()
                date_str = event_time.strftime("%m/%d/%Y %H:%M:%S.%f %z")
                row.insert(0,date_str)
                print('"'+'","'.join(row)+'"')
    except Exception as error:
        log("Encountered error :: %s " % error)

if __name__ == '__main__':

    rest_username='REST.splunk'

    '''
       Do not modify anything above this comment
    '''

    log("Executing report ingestion")

    try:

        '''
            Get input
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument("IN_REPORT_ID", help="Obtain Service Now report for provided report ID", type=str)
        args = parser.parse_args()

        '''
            Setup variables
        '''
        
        CSV_REPORT_NAME="servicenow_report-"+args.IN_REPORT_ID+".csv"
        API_URL="https://servicenow-host/sys_report_template.do?CSV&jvar_report_id="+args.IN_REPORT_ID
        APP_NAME="TA_servicenow-reports"
        local_filename = os.path.join('/opt','splunk', 'etc', 'apps', APP_NAME, 'lookups', CSV_REPORT_NAME)

        '''
            Get Login information from Splunk
        '''
        
        creds = get_credentials(rest_username)
        USER=creds[0]
        PASS=creds[1]

        '''
            Do the work
        '''
        get_CSV(API_URL,USER,PASS,local_filename)
        print_file(local_filename)

    except Exception as error:
        log("Encountered error :: %s " % error)