import urllib, urllib2, cookielib
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import re
import time

import web
# silence database logging
web.config.debug = False

import nltk

db = web.database(dbn='sqlite',db='/Users/Andrew/OKC_users_all.db')

class SearchHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.record_username = 0
        self.record_aso = 0
        self.record_location = 0
        self.username = ""
        self.data_count = 0
        self.user_data = []
    def handle_starttag(self, tag, attrs):
        for name,value in attrs:
            if name == 'class' and value == 'username':
                self.record_username = 1
            if name == 'class' and value == 'aso':
                self.record_aso = 1
            if name == 'class' and value == 'location':
                self.record_location = 1
    def handle_endtag(self, tag):
        if tag == 'span' and self.record_username:
            self.record_username = 0
        if tag == 'p' and self.record_aso == 1:
            self.record_aso = 0
        if tag == 'p' and self.record_location ==1:
            self.record_location = 0
    def handle_data(self, data):
        if self.record_username:
            self.username = data
            return
        if self.record_aso:
            self.user_data.append(data.strip())
            self.data_count += 1
        if self.record_location:
            state = data.strip().split(', ')[-1]
        #if self.data_count == 7:
            username = self.username
            age = self.user_data[0]
            sex = self.user_data[2]
            orient = self.user_data[4]
            status = self.user_data[6]
            essay_data = ""
            self.data_count = 0

            results = db.query("select count(*) as total_users from users where username=" + "'" + username + "'")
            num = results[0].total_users
            if num==0:
                print 'valid'
                db.insert('users',username=username,age=age,sex=sex,orient=orient,status=status,state=state,essay_data=essay_data)
            else:
                print 'invalid'
                
            self.username = ""
            self.user_data = []
            return


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

url = 'http://www.okcupid.com/match?filter1=1,63&filter2=2,18,18&filter3=5,31536000&filter6=35,0&lquery=%(zipcode)s&matchOrderBy=MATCH&custom_search=0&fromWhoOnline=0'

i = 0
while i<10000:
    try:
        req = urllib2.Request(url)

        resp = opener.open(req)

        parser = SearchHTMLParser()
        parser.feed(resp.read())
        print "Request %d finished."%i
    except:
        parser = SearchHTMLParser()
        print "ERROR ON %d"%i
    
    i = i+1
    time.sleep(3)

