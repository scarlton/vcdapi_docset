import os
import urlparse

from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

from vcd_api_guy.items import DocsetItem
from vcd_api_guy.items import SupportingFileItem
from vcd_api_guy import settings


class VcdSpider(CrawlSpider):
    name = "vcd_api"
    allowed_domains = ["pubs.vmware.com"]
    start_urls = [
        settings.DOMAIN + settings.BASE_PATH + "right-pane.html",
        settings.DOMAIN + settings.BASE_PATH + "doc-style.css",
        settings.DOMAIN + settings.BASE_PATH + "xml-style.css"
    ]

    def start_requests(self):
        requests = []
        for url in self.start_urls:
            requests.append(Request(url=url, headers={'Referer':settings.INITIAL_REFERRER}))

        return requests

    def parse(self, response):
        collected = []
        path = urlparse.urlsplit(response.url).path.replace(settings.BASE_PATH, '')

        # capture this file
        item = SupportingFileItem()
        item['path'] = path
        item['content'] = response.body
        collected.append(item)

        if os.path.splitext(path)[1] == '.html':
            sel = Selector(response)

            # follow API object type links
            for href in sel.xpath("//body/ul/li/a/@href").extract():
                url = urlparse.urljoin(response.url, href)
                collected.append(Request(url, callback=self.parse))

            # follow individual target links
            for href in sel.xpath("//table[not(@class='header-footer') and not(@class='ratingcontainer')]/tr/td/a/@href").extract():
              item['toc'] = True
              url = urlparse.urljoin(response.url, href)
              collected.append(Request(url, callback=self.parse_target))

        return collected

    def parse_target(self, response):
        path = urlparse.urlsplit(response.url).path.replace(settings.BASE_PATH, '')
        sel = Selector(response)

        # catpure target page
        docsetItem = DocsetItem()
        docsetItem['name'] = sel.xpath("//h1/text()").extract()[0]
        docsetItem['path'] = path
        docsetItem['url'] = response.url
        docsetItem['content'] = response.body

        # determine the item type based on the url we are scraping
        referrer = response.request.headers['Referer']
        if urlparse.urlparse(referrer).path.find('operations') != -1:
            docsetItem['item_type'] = 'Function'
        elif urlparse.urlparse(referrer).path.find('elements') != -1:
            docsetItem['item_type'] = 'Element'
        elif urlparse.urlparse(referrer).path.find('queries') != -1:
            docsetItem['item_type'] = 'Query'
        else:
            docsetItem['item_type'] = 'Type'

        return docsetItem