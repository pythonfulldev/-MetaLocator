# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HpMasterProjectItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    image = scrapy.Field()
    link = scrapy.Field()
    model = scrapy.Field()
    upc = scrapy.Field()
    ean = scrapy.Field()
    currencycode = scrapy.Field()
    locale = scrapy.Field()
    price = scrapy.Field()
    saleprice = scrapy.Field()
    sku = scrapy.Field()
    retailer_key = scrapy.Field()
    instore = scrapy.Field()
    shiptostore = scrapy.Field()
    shippingphrase = scrapy.Field()
    productstockstatus = scrapy.Field()
    categories = scrapy.Field()
    gallery = scrapy.Field()
    features = scrapy.Field()
    condition = scrapy.Field()



