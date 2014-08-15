# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
import os
import urlparse
import settings
from lxml import etree
from StringIO import StringIO
from scrapy import log

class SqlitePipeline(object):

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


class ContentPipeline(object):
    xpathToClean = [
        "head/script",
        "head/link",
        "feedbackhover",
        "id('ratingTop')",
        "id('ratingBottom')",
        "id('tb')"
    ]

    def process_item(self, item, spider):
        html = etree.parse(StringIO(item['content']), etree.HTMLParser())

        for xpath in self.xpathToClean:
            for el in html.xpath(xpath):
                el.getparent().remove(el)

        item['content'] = etree.tostring(html)
        return item


class FilePipeline(object):
    doc_dir = "Documents"

    def process_item(self, item, spider):
        # write local file if doesn't exist
        path = urlparse.urlsplit(item['url']).path.replace(settings.BASE_PATH, '')

        current_dir, current_file = os.path.split(path)
        if not os.path.exists(os.path.join(self.doc_dir, current_dir)):
            os.makedirs(os.path.join(self.doc_dir, current_dir))

        open(os.path.join(self.doc_dir, path), 'wb').write(item['content'])

        return item