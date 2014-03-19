# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
import settings
from scrapy import log

class VcdApiGuyPipeline(object):

    def __init__(self):
        log.msg('initializing sqlite db at %s/%s' % (settings.DOCSET_DB_PATH, settings.DOCSET_DB_NAME))

        os.chdir(settings.DOCSET_DB_PATH)
        self.db = sqlite3.connect(settings.DOCSET_DB_NAME)
        self.cursor = self.db.cursor()

        try: self.cursor.execute('DROP TABLE searchIndex;')
        except: pass
        self.cursor.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        self.cursor.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    def process_item(self, item, spider):
        log.msg('indexing %s: %s' % (item['item_type'], item['name']))
        self.cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (str(item.get('name')), str(item.get('item_type')), str(item.get('path'))))
        self.db.commit()
        return item