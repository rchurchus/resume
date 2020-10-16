#!/usr/bin/env python
'''
        Name ::         modify_asset_group
        Author ::       Robert Church
        Description ::  The purpose of this script is to connect to Qualys via
                        API and Add or Delete hosts from an Asset Group
        Version ::      0.1b - 2018-02-13 | Beta released by Robert Church
	                0.2b - 2018-03-08 | Accounted for subscriptions
 
'''
 
import sys
import lxml
import time
import qualysapi
import argparse
import xmltodict
from collections import OrderedDict
import pprint
 
parser = argparse.ArgumentParser(description='Modify Asset Group Hosts')
parser.add_argument('--asset_group', dest='GROUPID', metavar='N', type=int, help='Asset Group ID')
parser.add_argument('--host_ip', dest='HOSTIP', metavar='1.1.1.1', help='Host IP Address')
parser.add_argument('--add', dest='ADD', help='Add host to asset group', action="store_true")
parser.add_argument('--delete', dest='DELETE', help='Delete host from asset group', action="store_true")
 
args = parser.parse_args()
 
if (args.ADD and args.DELETE):
        print("Must specify add or remove, not both")
        parser.print_help()
        exit(0)
 
if (args.ADD is None or args.DELETE is None):
        print("Must specify add or remove")
        parser.print_help()
        exit(0)
 
if (args.GROUPID is None or args.HOSTIP is None):
        parser.print_help()
        exit(0)
 
if type(args.GROUPID) is int:
        groupid = args.GROUPID
else:
        print("Group ID must be an integer")
 
 
# Initialize connection
qgc = qualysapi.connect('config.txt')
 
def check_if_in_subscription(IP):
 
        # Check if IP address is present in subscription
        call = '/api/2.0/fo/asset/ip/'
        parameters = {'action': 'list', 'ips': args.HOSTIP}
        xml_output = qgc.request(call, parameters)
        data = xmltodict.parse(xml_output[2:-1].replace('\\n', '\n'))
        response = OrderedDict(data['IP_LIST_OUTPUT']['RESPONSE'])
 
        if ('IP_SET' in response.keys()):
                return True
        return False
 
def add_ip_to_subscription(IP):
       
        # Add IPs into subscription
        call = '/api/2.0/fo/asset/ip/'
        parameters = {'action': 'add', 'enable_vm': '1', 'ips': args.HOSTIP}
        xml_output = qgc.request(call, parameters)
        data = xmltodict.parse(xml_output[2:-1].replace('\\n', '\n'))
        status = data['SIMPLE_RETURN']['RESPONSE']['TEXT']
        return(status)
 
def add_ip_to_asset_group(HOSTIP, GROUPID):
        # Add IPs into Asset Group
        call = '/api/2.0/fo/asset/group/'
        parameters = {'id': GROUPID, 'action': 'edit', 'add_ips': HOSTIP}
        xml_output = qgc.request(call, parameters)
        data = xmltodict.parse(xml_output[2:-1].replace('\\n', '\n'))
        status = data['SIMPLE_RETURN']['RESPONSE']['TEXT']
        print("Action :: Add (%s) into Asset Group" % HOSTIP)
        if (status == "Asset Group Updated Successfully"):
                print("Output :: Successfully added %s to Asset Group\n" % HOSTIP)
        else:
                print("Output :: %s\n" % status)
                exit(1)
 
def remove_ip_from_asset_group(HOSTIP, GROUPID):
        # Add IPs into Asset Group
        call = '/api/2.0/fo/asset/group/'
        parameters = {'id': GROUPID, 'action': 'edit', 'remove_ips': HOSTIP}
        xml_output = qgc.request(call, parameters)
        data = xmltodict.parse(xml_output[2:-1].replace('\\n', '\n'))
        status = data['SIMPLE_RETURN']['RESPONSE']['TEXT']
        print("Action :: Remove (%s) from Asset Group" % HOSTIP)
        if (status == "Asset Group Updated Successfully"):
                print("Output :: Successfully removed %s from Asset Group\n" % HOSTIP)
        else:
                print("Output :: %s\n" % status)
                exit(1)
 
try:
        print("---------------------------")
        if (args.ADD):
                ip_in_sub = check_if_in_subscription(args.HOSTIP)
                if (ip_in_sub == True):
                        add_ip_to_asset_group(args.HOSTIP, args.GROUPID)
                else:
                        print("Action :: Add (%s) into Qualys Subscription" % args.HOSTIP)
                        status = add_ip_to_subscription(args.HOSTIP)
                        if(status == 'IPs successfully added to Vulnerability Management'):
                                print("Output :: (%s) Has been added successfully\n" % args.HOSTIP)
                        else:
                                print("Output :: Error encountered (%s)\n" % status)
                                exit(1)
                        # Give Qualy stime to process subscription addition before proceeding
                        ip_in_sub = False
                        counter = 1
                        max_tries = 5
                        while True:
                                ip_in_sub = check_if_in_subscription(args.HOSTIP)
                                if (ip_in_sub == True):
                                        add_ip_to_asset_group(args.HOSTIP, args.GROUPID)
                                        break
                                else:
                                        if (counter <= max_tries):
                                                print("Subscription not updated yet, waiting 30 seconds before next attempt (%s/%s)" % counter, max_tries)
                                                counter = counter + 1
                                                time.sleep(30)
                                        else:
                                                print("Unable to verify IP in subscription.  It may not have inserted into subscription properly.")
                                                exit(1)
        elif (args.DELETE):
                remove_ip_from_asset_group(args.HOSTIP, args.GROUPID)
 
        print("---------------------------")
 
except:
 
        e = sys.exc_info()[0]
        print(e)
