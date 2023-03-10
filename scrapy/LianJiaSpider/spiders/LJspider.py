import scrapy
import re
from items import LianjiaspiderItem
from scrapy.exceptions import CloseSpider


class LjspiderSpider(scrapy.Spider):
    name = 'LJspider'
    allowed_domains = ['xa.lianjia.com']
    page = 1
    start_urls = ['https://xa.lianjia.com/ershoufang/pg' + str(page) + 'co32/']
    BASE_url = 'https://xa.lianjia.com/'
    maxPage = 100

    def parse(self, response):
        inner_urls = response.xpath(
            '//ul[@class="sellListContent"]//div[@class="info clear"]/div[@class="title"]/a/@href').getall()
        if len(inner_urls) > 0:
            print(f'Current page: {self.page}')
            for url in inner_urls:
                yield scrapy.Request(url=url, callback=self.infoparse)

            if self.page < self.maxPage:
                self.page += 1
                next_url = response.url[:36] + str(self.page) + response.url[-5:]
                yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            self.maxPage = -1

    def infoparse(self, response):
        _id = response.url[34:-5]
        print(f'\tParsing id: {_id}')

        price_box = response.xpath('//div[@class="overview"]/div[@class="content"]//div[@class="price "]')
        totalPrice = price_box.xpath('./span[@class="total"]/text()').get()
        unitPrice = price_box.xpath('.//span[@class="unitPriceValue"]/text()').get()

        areaName = response.xpath(
            '//div[@class="aroundInfo"]//div[@class="areaName"]/span[@class="info"]/a/text()').getall()
        region = areaName[0]
        if len(areaName) > 1:
            garden = areaName[1]
        else:
            garden = None

        house_info = response.xpath('//div[@class="m-content"]//div[@class="introContent"]')
        base_info = house_info.xpath('./div[@class="base"]//li')
        layout = base_info.xpath('./span[text()="房屋户型"]/following-sibling::text()').get()
        floor = base_info.xpath('./span[text()="所在楼层"]/following-sibling::text()').get()
        area = base_info.xpath('./span[text()="建筑面积"]/following-sibling::text()').get()
        type = base_info.xpath('./span[text()="户型结构"]/following-sibling::text()').get()
        building = base_info.xpath('./span[text()="建筑类型"]/following-sibling::text()').get()
        direction = base_info.xpath('./span[text()="房屋朝向"]/following-sibling::text()').get()
        structure = base_info.xpath('./span[text()="建筑结构"]/following-sibling::text()').get()
        renovation = base_info.xpath('./span[text()="装修情况"]/following-sibling::text()').get()
        stairway = base_info.xpath('./span[text()="梯户比例"]/following-sibling::text()').get()
        heating = base_info.xpath('./span[text()="供暖方式"]/following-sibling::text()').get()
        elevator = base_info.xpath('./span[text()="配备电梯"]/following-sibling::text()').get()

        transaction_info = house_info.xpath('./div[@class="transaction"]//li')
        usage = transaction_info.xpath('./span[text()="房屋用途"]/following-sibling::span[not(@*)]/text()').get()
        year = transaction_info.xpath('./span[text()="房屋年限"]/following-sibling::span[not(@*)]/text()').get()
        # ownership = transaction_info.xpath('./span[text()="产权所属"]/following-sibling::span[not(@*)]/text()').get()
        # mortgage = transaction_info.xpath('./span[text()="抵押信息"]/following-sibling::span[not(@*)]/text()').get()

        totalPrice = float(totalPrice)
        unitPrice = float(unitPrice)
        area = float(re.search(r'(\.|\d)+', area).groups()[0])
        item = LianjiaspiderItem(
            _id=_id,
            totalPrice=totalPrice,
            unitPrice=unitPrice,
            region=region,
            garden=garden,
            layout=layout,
            floor=floor,
            area=area,
            type=type,
            building=building,
            direction=direction,
            structure=structure,
            renovation=renovation,
            stairway=stairway,
            heating=heating,
            elevator=elevator,
            usage=usage,
            year=year,
        )
        yield item
