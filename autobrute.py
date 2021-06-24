#! /usr/bin/env python3

import requests
import sys
from requests_ntlm2 import HttpNtlmAuth
from optparse import OptionParser
from utils import messages

testurl = "http://192.168.2.211/foo.txt"

def sendrequest(url, username, password, domain, log):
    auth=HttpNtlmAuth("{}\\{}".format(domain, username), password)
    resp = requests.get(url, auth=auth)

    if resp.status_code == 200:
        log.success("VALID Credentials FOUND: {}\\{}: {}".format(domain, username, password))
    else:
        log.error("INVALID Credentials: {}\\{}: {}".format(domain, username, password))
   
def main():
    log = messages.message()
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--targeturl", dest="targeturl", help="This URL (with complete URI) to the target site requesting authentication.")
    parser.add_option("-u", "--userfile", dest="userfile", help="Required. A list of users to use for authentication.")
    parser.add_option("-p", "--passfile", dest="passfile", help="Required. A list of passwords to use for authentication attempts.")
    parser.add_option("-v", "--verbose", action="store_true", default=False, help="Verbose output. Show each individual test.")
    (options, args) = parser.parse_args()

    errors = []
    errorfound = False
    if options.userfile is None:
        errors.append("RTFMException. -u is Required.")
        errorfound = True

    if options.passfile is None:
        errors.append("RTFMException. -p is Required.")
        errorfound = True

    if options.targeturl is None:
        errors.append("RTFMException. -t is Required.")
        errorfound = True

    if errorfound:
        for msg in errors:
            log.error(msg, False)
        sys.exit(1)
    # sendrequest(testurl, "lowpriv1", "Password1", "lab.com", log)
    # sendrequest(testurl, "lowpriv2", "Password1", "lab.com", log)

if __name__ == '__main__':
    main()
