# - * - coding: utf-8 -*-#
from __future__ import absolute_import, division, unicode_literals

import scrapy
import re
from scrapy import Request
import urlparse
from HP_Master_Project.items import HpMasterProjectItem


def extract_first(selector_list, default=None):
    for x in selector_list:
        return x.extract()
    else:
        return default


def clean_text(self, text):
    text = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
    text = re.sub("&nbsp;", " ", text).strip()

    return re.sub(r'\s+', ' ', text)


class ConnectionSpider(scrapy.Spider):
    name = "connection_products"
    allowed_domains = ['https://www.connection.com']

    SEARCH_URL = 'https://www.connection.com/IPA/Shop/Product/Search?SearchType=1&term=hp'

    def start_requests(self):
        yield scrapy.Request(url=self.SEARCH_URL, callback=self.parse_links)

    def parse_links(self, response):
        total_match = re.search('of (\d+) Results', response.body)
        total_match = int(total_match.group(1)) if total_match else 0

        result_per_page = re.search('1 - (\d+) of', response.body)
        result_per_page = int(result_per_page.group(1)) if result_per_page else 12

        page_count = total_match / result_per_page + 1

        total_page_links = []
        for i in range(1, int(page_count) + 1):
            offset = '#{page_num}~Best+Matches~{result_per_page}~List'.format(page_num=i,
                                                                              result_per_page=result_per_page)
            page_link = self.SEARCH_URL + offset
            total_page_links.append(page_link)

        for total_page_link in total_page_links:
            yield Request(url=total_page_link, callback=self.parse_link, dont_filter=True)

    def parse_link(self, response):
        product_links = response.xpath('//div[@class="product-name-list"]/a/@href').extract()

        for product_link in product_links:
            prod_link = urlparse.urljoin(response.url, product_link)
            yield Request(url=prod_link, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        product = HpMasterProjectItem()

        # Parse name
        name = self._parse_name(response)
        product['name'] = name

        # Parse image
        image = self._parse_image(response)
        product['image'] = image

        # Parse link
        product['link'] = response.url

        # Parse model
        model = self._parse_model(response)
        product['model'] = model

        # Parse upc
        upc = self._parse_upc(response)
        product['upc'] = upc

        # Parse ean
        product['ean'] = None

        # Parse currencycode
        product['currencycode'] = 'USD'

        # Set locale
        product['locale'] = 'en-US'

        # Parse price
        price = self._parse_price(response)
        product['price'] = price

        # Parse sale price
        product['saleprice'] = price

        # Parse sku
        sku = self._parse_sku(response)
        product['sku'] = sku

        # Parse retailer_key
        product['retailer_key'] = None

        # Parse in_store
        in_store = self._parse_instore(response)
        product['instore'] = in_store

        # Parse ship to store
        ship_to_store = self._parse_shiptostore(response)
        product['shiptostore'] = ship_to_store

        # Parse shipping phrase
        shipping_phrase = self._parse_shippingphrase(response)
        product['shippingphrase'] = shipping_phrase

        # Parse stock status
        stock_status = self._parse_stock_status(response)
        product['productstockstatus'] = stock_status

        # Parse gallery
        product['gallery'] = None

        # Parse features

        features = self._parse_features(response)
        product['features'] = features

        # Parse condition
        product['condition'] = 1

        return product

    @staticmethod
    def _parse_name(response):
        name = extract_first(response.xpath('//h1[@class="pagetitle"]/text()'))
        return name

    @staticmethod
    def _parse_image(response):
        image_url = extract_first(response.xpath('//a[@item-prop="image"]/@href'))
        return image_url

    def _parse_model(self, response):
        model = extract_first(response.xpath('//span[@itemprop="mpn"]/text()'))
        return clean_text(self, model)

    @staticmethod
    def _parse_upc(response):
        return None

    @staticmethod
    def _parse_price(response):
        price = extract_first(response.xpath('//span[@class="product-price"]'
                                             '/span[@class="priceDisplay"]/text()'))
        return float(price.replace("$", ""))

    def _parse_sku(self, response):
        sku = extract_first(response.xpath('//span[@itemprop="sku"]/text()'))
        return clean_text(self, sku)

    def _parse_instore(self, response):
        if self._parse_price(response):
            return 1

        return 0

    def _parse_shiptostore(self, response):
        if self._parse_shippingphrase(response):
            return 1

        return 0

    @staticmethod
    def _parse_shippingphrase(response):
        shipping_phrase = extract_first(response.xpath('//span[@id="productEstimatedShipping"]/text()'))
        return shipping_phrase

    @staticmethod
    def _parse_stock_status(response):
        stock_value = 4
        stock_status = extract_first(response.xpath('//span[@id="productAvailability"]/text()'))
        stock_status = stock_status.lower()

        if stock_status == 'out of stock':
            stock_value = 0

        if stock_status == 'in stock':
            stock_value = 1

        if stock_status == 'call for availability':
            stock_value = 2

        if stock_status == 'discontinued':
            stock_value = 3

        return stock_value

    def _parse_features(self, response):
        features = []
        features_name = response.xpath('//ul[@id="productSpecsContainer"]'
                                       '/li//label[contains(@for, "product_spec")]/text()').extract()
        for f_name in features_name:
            f_content = response.xpath('//ul[@id="productSpecsContainer"]'
                                       '/li/div[contains(@id, "product_spec")]'
                                       '/*[@aria-label="%s"]'
                                       '//text()' % f_name).extract()
            if len(f_content) > 1:
                f_content = " ".join(f_content)
                f_content = clean_text(self, f_content)
                f_content = [f_content]
            else:
                f_content = f_content[0]
                f_content = clean_text(self, f_content)

            feature = (f_name, f_content)
            features.append(feature)
        return features
