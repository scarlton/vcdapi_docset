# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
import urlparse
import urllib
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
        if 'item_type' in item:
            log.msg('indexing %s: %s' % (item['item_type'], item['name']))
            self.cursor.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (str(item.get('name')), str(item.get('item_type')), str(item.get('path'))))
            self.db.commit()
        return item


class ContentPipeline(object):
    xpathToClean = [
        "//script",
        "//head/link[not(@href='doc-style.css') and not(@href='../doc-style.css') and not(@href='../xml-style.css')]",
        "//head/style",
        "//table[@class='header-footer']",
        "id('feedbackhover')",
        "id('ratingTop')",
        "id('ratingBottom')",
        "id('tb')"
    ]

    def process_item(self, item, spider):
        if os.path.splitext(item['path'])[1] == '.html':
            html = etree.parse(StringIO(item['content']), etree.HTMLParser())

            for xpath in self.xpathToClean:
                for el in html.xpath(xpath):
                    el.getparent().remove(el)

            # add Dash TOC
            if 'toc' in item and item['toc']:
                for el in html.xpath("//table[not(@class='header-footer') and not(@class='ratingcontainer')]/tr/td/a"):
                    itemType = 'Type'
                    if item['path'].find('operations') != -1:
                        itemType = 'Function'
                    elif item['path'].find('elements') != -1:
                        itemType = 'Element'
                    elif item['path'].find('queries') != -1:
                        itemType = 'Query'

                    name = "//apple_ref/cpp/%s/%s" % (itemType, urllib.quote(el.text, ''))
                    el.set('name', name)
                    el.set('class', 'dashAnchor')

            # rewrite xsd links absolute
            for el in html.xpath("//dd/a[contains(@href, '.xsd')]"):
                href = urlparse.urljoin(item['url'], el.get('href'))
                el.set('href', href)

            item['content'] = etree.tostring(html)

        return item


class FilePipeline(object):
    doc_dir = "Documents"

    def process_item(self, item, spider):
        # write local file if doesn't exist

        current_dir, current_file = os.path.split(item['path'])
        if not os.path.exists(os.path.join(self.doc_dir, current_dir)):
            os.makedirs(os.path.join(self.doc_dir, current_dir))

        open(os.path.join(self.doc_dir, item['path']), 'wb').write(item['content'])

        return item