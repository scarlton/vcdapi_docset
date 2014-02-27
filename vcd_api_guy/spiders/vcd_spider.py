from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy import log

from vcd_api_guy.items import VcdApiGuyItem

import os
import urlparse

domain = "https://www.vmware.com"
base_path = "/support/vcd/doc/rest-api-doc-1.5-html/"

class VcdSpider(CrawlSpider):
    name = "vcd_api"
    allowed_domains = ["www.vmware.com"]
    start_urls = [
        "https://www.vmware.com/support/vcd/doc/rest-api-doc-1.5-html/right-pane.html",
        "https://www.vmware.com/support/vcd/doc/rest-api-doc-1.5-html/landing-operations.html",
        "https://www.vmware.com/support/vcd/doc/rest-api-doc-1.5-html/landing-elements.html",
        "https://www.vmware.com/support/vcd/doc/rest-api-doc-1.5-html/landing-types.html"
    ]

    rules = (Rule (SgmlLinkExtractor(restrict_xpaths='//table[not(@class = "header-footer")]'), callback="parse_entry", follow= True),)

    # def parse(self, response):
    #     #write local file if doesn't exist
    #     #filename = response.url.split("/")[-1]
    #     #open(filename, 'wb').write(response.body)

    #     #find entry links and create new requests
    #     sel = Selector(response)
    #     objects = sel.xpath('//table[not(@class = "header-footer")]//a')
    #     reqs = []
    #     for obj in objects:
    #         req = Request(urlparse.urljoin(response.url, obj.xpath('@href')), callback=self.parse_guy)
    #         if urlparse.urlparse(response.url)['path'].find('operations') != -1:
    #             req.meta['item_type'] = 'Function'
    #         elif urlparse.urlparse(response.url)['path'].find('elements') != -1:
    #             req.meta['item_type'] = 'Element'
    #         else:
    #             req.meta['item_type'] = 'Type'
    #         reqs.append()

    #     return reqs

    def parse_entry(self, response):
        #write local file if doesn't exist
        path = urlparse.urlsplit(response.url).path.replace(base_path, '')

        current_dir, current_file = os.path.split(path)
        if not os.path.exists(current_dir):
            os.makedirs(current_dir)

        open(path, 'wb').write(response.body)

        sel = Selector(response)
        item = VcdApiGuyItem()
        item['name'] = sel.xpath("//h1/text()").extract()
        item['path'] = path

        referrer = response.request.headers['Referer']
        if urlparse.urlparse(referrer).path.find('operations') != -1:
            item['item_type'] = 'Function'
        elif urlparse.urlparse(referrer).path.find('elements') != -1:
            item['item_type'] = 'Element'
        else:
            item['item_type'] = 'Type'

        return item