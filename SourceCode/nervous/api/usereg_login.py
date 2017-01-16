import hashlib
import urllib2

def md5_hash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

def check(username, password):
    return True
