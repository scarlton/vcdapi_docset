# Scrapy settings for vcd_api_guy project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'vcd_api_guy'

SPIDER_MODULES = ['vcd_api_guy.spiders']
NEWSPIDER_MODULE = 'vcd_api_guy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'vcd_api_guy (+http://www.yourdomain.com)'


ITEM_PIPELINES = {
    'vcd_api_guy.pipelines.SqlitePipeline':10,
    'vcd_api_guy.pipelines.ContentPipeline':20,
    'vcd_api_guy.pipelines.FilePipeline':30
}


DOMAIN = "http://pubs.vmware.com"
BASE_PATH = "/vcd-810/topic/com.vmware.vcloud.api.reference.doc_20_0/doc/"
INITIAL_REFERRER = DOMAIN + BASE_PATH + "index.html"

DOCSET_DB_PATH = 'vCloud_Director.docset/Contents/Resources'
DOCSET_DB_NAME = 'docSet.dsidx'
