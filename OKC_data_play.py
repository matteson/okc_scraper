import web
import time
import nltk
from nltk_utils import *

# silence database logging
web.config.debug = False

db = web.database(dbn='sqlite',db='/Users/Andrew/OKC_users_all.db')

# sex summary
maleQ = db.query("SELECT COUNT(*) AS num FROM users WHERE sex = 'M'")
male_num = maleQ[0].num
femaleQ = db.query("SELECT COUNT(*) AS num FROM users WHERE sex = 'F'")
female_num = femaleQ[0].num

# orient summary
strQ = db.query("SELECT COUNT(*) AS num FROM users WHERE orient = 'Straight'")
str_num = strQ[0].num
biQ = db.query("SELECT COUNT(*) AS num FROM users WHERE orient = 'Bi'")
bi_num = biQ[0].num
gayQ = db.query("SELECT COUNT(*) AS num FROM users WHERE orient = 'Gay'")
gay_num = gayQ[0].num

# status summary
singleQ = db.query("SELECT COUNT(*) AS num FROM users WHERE status = 'Single'")
single_num = singleQ[0].num
availQ = db.query("SELECT COUNT(*) AS num FROM users WHERE status = 'Available'")
avail_num = availQ[0].num
seeingQ = db.query("SELECT COUNT(*) AS num FROM users WHERE status = 'Seeing Someone'")
seeing_num = seeingQ[0].num
marriedQ = db.query("SELECT COUNT(*) AS num FROM users WHERE status = 'Married'")
married_num = marriedQ[0].num

# print statuses
print '''
Sex summary:
Male:            %(male)s
Female:      :   %(female)s'''%{"male":male_num,
                                "female":female_num
                                }
print '''
Orientation summary:
Straight:         %(straight)s
Bi:       :       %(bi)s
Gay:              %(gay)s'''%{"straight":str_num,
                              "bi":bi_num,
                              "gay":gay_num
                                }
print '''
Status summary:
Single:           %(single)s
Seeing Someone:   %(seeing)s
Avalable:         %(avail)s
Married:          %(married)s'''%{"single":single_num,
                                  "seeing":seeing_num,
                                  "avail":avail_num,
                                  "married":married_num
                                  }
print '''
'''

curr = time.time()
# compile token set
user_rows = db.select('users')
okc_tokens = []

for user in user_rows:
    data = user['essay_data']
    user_tokens = nltk.word_tokenize(data.encode('utf-8'))
    okc_tokens.extend(user_tokens)

okc_corpus = nltk.text.Text(okc_tokens)

print time.time()-curr

fdist = nltk.FreqDist(okc_corpus)
con_words = sorted([w for w in set(okc_corpus) if len(w)>7 and fdist[w] > 7])

okc_corpus.concordance('dylan')

print unusual_words(con_words)
