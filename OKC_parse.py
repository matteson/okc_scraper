import urllib, urllib2, cookielib
import nltk
import time
import web
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint


class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.recording = 0
        self.data = []
        
    def handle_starttag(self, tag, attrs):
        if tag != 'div':
            return
        if self.recording:
            self.recording +=1
            return
        for name,value in attrs:
            if name == 'id' and not (value.find('essay_text') == -1): # want to check value for essay_text here
                self.recording = 1
                break
            else:
                return

    def handle_endtag(self, tag):
        if tag == 'div' and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)

# initialize parser
parser = MyHTMLParser()

# setup credentials and url requests
# cookie storage
cj = cookielib.CookieJar()
opener = urllib2.build_opener(
    urllib2.HTTPCookieProcessor(cj),
    urllib2.HTTPRedirectHandler
    )
# Useragent
opener.addheaders.append(('User-agent','Mozilla/4.0'))

url = 'http://www.okcupid.com/login'
login_data = urllib.urlencode({
    'username':'data_curious',
    'password':'notapassword',
    })

req = urllib2.Request(url,login_data)
resp = opener.open(req)

# open user database
db = web.database(dbn='sqlite',db='/Users/Andrew/OKC_users_all.db')

# get a user as test data

user_rows = db.select('users',where="essay_data=''", order="username ASC")
#user_rows = db.select('users')
user = user_rows.i.next()

while user:
    curr_time = time.time()
    url = 'http://www.okcupid.com/profile/' + str(user.username)
    req = urllib2.Request(url)

    resp = opener.open(req)
    content = resp.read()

    ##
    try:
        parser.feed(content)
        result = parser.data
        parser.data = []
        result_str = ('').join(result)
        uresult = result_str.decode('utf8')

        db.update('users',where="username = '%(user)s'"%{"user":str(user.username)},essay_data=uresult) 
    except:
        print "Error in parser for user %(username)s"%{"username":str(user.username)}
        parser = MyHTMLParser()
        
    user = user_rows.i.next()
    print time.time() - curr_time
    time.sleep(3)
