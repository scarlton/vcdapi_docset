# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class VcdApiGuyItem(Item):
    # define the fields for your item here like:
    # name = Field()
    name = Field()
    item_type = Field()
    path = Field()
    url = Field()
    content = Field()