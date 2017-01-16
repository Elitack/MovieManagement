import json
import codecs

from scrapy import log
from twisted.enterprise import adbapi
from scrapy.http import Request

import urllib
import MySQLdb
import MySQLdb.cursors

class DoubanmoivePipeline(object):

    def __init__(self):
        self.file = codecs.open('douban_data.json', mode='wb', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))

        return item
		
class DoPipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                db = 'liu',
                user = 'root',
                passwd = '951031',
                cursorclass = MySQLdb.cursors.DictCursor,
                charset = 'utf8',
                use_unicode = False
        )
		
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self,tx,item):
        tx.execute("select * from doubanmoive where m_name= %s",(item['name']))
        result=tx.fetchone()
        log.msg(result,level=log.DEBUG)
        print result
        if result:
            log.msg("Item already stored in db:%s" % item,level=log.DEBUG)
        else:
            classification=actor=''
            lenClassification=len(item['classification'])
            lenActor=len(item['actor'])
            for n in xrange(lenClassification):
                classification+=item['classification'][n]
                if n<lenClassification-1:
                    classification+='/'
            for n in xrange(lenActor):
                actor+=item['actor'][n]
                if n<lenActor-1:
                    actor+='/'
            site= item['img'][0]
            str = site.split('/');
            print str
            path = str[-1]
            print 'local img path %s'%(path)
            print '--------------------download img %s'%(site)
            data = urllib.urlopen(site).read()
            newfile = open(path,"wb")
            newfile.write(data)
            newfile.close()
            tx.execute(\
                "insert into doubanmoive (m_name,m_year,m_score,m_director,m_classification,m_actor,m_img,m_local_img,m_num,m_link,m_commentnum,m_commentweb,m_story) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
                 ("".join(item['name']), "".join(item['year']), "".join(item['score']), "".join(item['director']), classification, actor,site,path,"".join(item['num']),"".join(item['link']),"".join(item['commentnum']),"".join(item['commentweb']),"".join(item['story'])))
            log.msg("Item stored in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)
