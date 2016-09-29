from scrapy.item import Item, Field

class DocsetItem(Item):
    name = Field()
    item_type = Field()
    path = Field()
    url = Field()
    content = Field()

class SupportingFileItem(Item):
    path = Field()
    content = Field()
    toc = Field()
