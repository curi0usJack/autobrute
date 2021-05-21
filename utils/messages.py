#!/usr/bin/python3 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class message:
    def ok(self, message):
        print(bcolors.OKBLUE + "[*] {}".format(message) + bcolors.ENDC)

    def warn(self, message):
        print(bcolors.WARNING + "[!] {}".format(message) + bcolors.ENDC)

    def success(self, message):
        print(bcolors.OKGREEN + "[+] {}".format(message) + bcolors.ENDC)

    def error(self, message):
        print(bcolors.FAIL + "[!] {}".format(message) + bcolors.ENDC)
