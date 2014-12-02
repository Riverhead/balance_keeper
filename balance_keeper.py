#!/usr/bin/env python
# coding=utf8

# This is a watchdog script which connects to a delegate periodically to verify that it is up and running,
# and to do some basic maintenance tasks if the delegate is not ready to sign blocks and report if it is
# unhealthy

import requests
import sys
import os
import json
import getpass
import time
import datetime
from pprint import pprint

BTS_PRECISION = 100000

config_data = open('config.json')
config = json.load(config_data)
config_data.close()

auth = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
url = config["bts_rpc"]["url"]

WALLET_NAME = config["wallet_name"]

DELEGATE_NAME = config["delegate_name"]
PAYTO = config["payto_account"]
THRESH = config["balance_threshold"]

def parse_date(date):
  return datetime.datetime.strptime(date, "%Y%m%dT%H%M%S")

def call(method, params=[]):
  headers = {'content-type': 'application/json'}
  request = {
          "method": method,
          "params": params,
          "jsonrpc": "2.0",
          "id": 1
          }

  while True:
    try:
      response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
      result = json.loads(vars(response)["_content"])
      #print "Method:", method
      #print "Result:", result
      return result
    except:
      print "Warnning: rpc call error, retry 5 seconds later"
      time.sleep(5)
      continue
    break  
  return None

while True:
  try:
    os.system("clear")
    print("\nRunning Balance Keeper")
 
    response = call("wallet_get_account", [DELEGATE_NAME] )
    if "error" in response:
      print("FATAL: Failed to get info:")
      print(result["error"])
      exit(1)
    response = response["result"]

    balance = response["delegate_info"]["pay_balance"] / BTS_PRECISION

    print ("Balance for %s is currently: %s BTS" % (DELEGATE_NAME, balance))

    if balance > 2000:
       print("wallet_delegate_withdraw_pay %s, %s, %s" % (DELEGATE_NAME, PAYTO, THRESH))
       response = call("wallet_delegate_withdraw_pay", [DELEGATE_NAME, PAYTO, THRESH])
    
    time.sleep(1010)
  except:
    time.sleep(1010)
