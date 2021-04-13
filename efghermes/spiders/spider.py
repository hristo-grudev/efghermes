import scrapy

from scrapy.loader import ItemLoader

from ..items import EfghermesItem
from itemloaders.processors import TakeFirst
import requests

base_url = "https://www.efghermes.com/account/searchcorporatenews"

base_payload = "Year=&News=&lang=en&sectiontypeId=65&Page={}"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://www.efghermes.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.efghermes.com/en/newsroom-km',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'TS017c20d9=013ae8bf25c22586d529ef79558fe0d2cf55edd6034683f3aa900abe1a40c71be61f288f39d206766930780d6d4b613d5198944652'
}


class EfghermesSpider(scrapy.Spider):
	name = 'efghermes'
	page = 1
	start_urls = ['https://www.efghermes.com/en/newsroom-km']

	def parse(self, response):
		payload = base_payload.format(self.page)
		data = requests.request("POST", base_url, headers=headers, data=payload)

		raw_data = scrapy.Selector(text=data.text)
		post_links = raw_data.xpath('//a[contains(@class, "box__meta")]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) > 1:
			self.page += 1
			yield from response.follow_all(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		print(response)
		title = response.xpath('//h3/text()').get()
		description = response.xpath('//div[@class="no-free-will"]//text()[normalize-space() and not(ancestor::h3)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = response.xpath('//h3/following::p[1]/text()').get()

		item = ItemLoader(item=EfghermesItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
