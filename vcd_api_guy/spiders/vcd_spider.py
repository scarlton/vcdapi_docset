from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
import urlparse

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

from vcd_api_guy.items import VcdApiGuyItem
from vcd_api_guy import settings


class VcdSpider(CrawlSpider):
    name = "vcd_api"
    allowed_domains = ["pubs.vmware.com"]
    start_urls = [
        # settings.DOMAIN + settings.BASE_PATH + "right-pane.html"
        settings.DOMAIN + settings.BASE_PATH + "landing-user_operations.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-user_elements.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-user_types.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-user_typed-queries.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-admin_types.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-admin_elements.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-admin_operations.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-admin_typed-queries.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-extension_operations.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-extension_elements.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-extension_types.html",
        settings.DOMAIN + settings.BASE_PATH + "landing-extension_typed-queries.html"
    ]

    rules = (Rule (SgmlLinkExtractor(restrict_xpaths='//table[not(@class = "header-footer")]'), callback="parse_entry", follow= True),)

    def start_requests(self):
        requests = []
        for url in self.start_urls:
            requests.append(Request(url=url, headers={'Referer':settings.INITIAL_REFERRER}))

        return requests

    def parse_entry(self, response):
        path = urlparse.urlsplit(response.url).path.replace(settings.BASE_PATH, '')

        sel = Selector(response)
        item = VcdApiGuyItem()
        item['name'] = sel.xpath("//h1/text()").extract()[0]
        item['path'] = path
        item['url'] = response.url
        item['content'] = response.body

        # determine the item type based on the url we are scraping
        referrer = response.request.headers['Referer']
        if urlparse.urlparse(referrer).path.find('operations') != -1:
            item['item_type'] = 'Function'
        elif urlparse.urlparse(referrer).path.find('elements') != -1:
            item['item_type'] = 'Element'
        elif urlparse.urlparse(referrer).path.find('queries') != -1:
            item['item_type'] = 'Query'
        else:
            item['item_type'] = 'Type'

        return item