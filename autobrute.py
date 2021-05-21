#! /usr/bin/env python3

import requests
from requests_ntlm2 import HttpNtlmAuth

from utils import messages

testurl = "http://192.168.2.211/foo.txt"

def sendrequest(url, username, password, domain, log):
    auth=HttpNtlmAuth("{}\\{}".format(domain, username), password)
    resp = requests.get(url, auth=auth)
    print(resp.status_code)
    
def main():
    log = messages.message()
    sendrequest(testurl, "lowpriv1", "Password1", "lab.com", log)

if __name__ == '__main__':
    main()
