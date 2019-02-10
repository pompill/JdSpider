from scrapy.spiders import Spider
import scrapy

# 第三方包
from lxml import etree
import requests
import hashlib
import re
import json

# 内置包
import time

# 项目内部包
from jd.items import JdItem

# 第三方插件
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class JdSpider(Spider):
    name = "Jd"
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    start_url = "https://www.jd.com/?cu=true&utm_source=baidu-pinzhuan&utm_medium=cpc&utm_campaign=t_288551095_baidupinzhuan&utm_term=0f3d30c8dba7459bb52f2eb5eba8ac7d_0_0ba6a4139a764dcfa26b16e2ecb4dd91"
    browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    json_url = "https://c0.3.cn/stock?skuId={}&cat=737,794,878&venderId={}"
    tail = "&area=1_72_4137_0&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=1059759470&pdpin="

    def start_requests(self):
        self.browser.get(url=self.start_url)
        wait = WebDriverWait(self.browser, 10)
        for _ in range(1):
            button = wait.until(
                ec.visibility_of_element_located((By.XPATH, '//ul[@class="JS_navCtn cate_menu"]/li[{}]'.format(1))))
            ActionChains(self.browser).move_to_element(button).perform()
            time.sleep(3)
            html = self.browser.page_source
            selector = etree.HTML(html)
            href = selector.xpath('//dd[@class="cate_detail_con"]/a/@href')
            print(href)
            for url in href:
                if url.startswith('http'):
                    yield scrapy.Request(url=url, headers=self.header, callback=self.get_url)
                elif url.startswith('//'):
                    url = 'https:' + url
                    yield scrapy.Request(url=url, headers=self.header, callback=self.get_url)

    def get_url(self, response):
        selector = etree.HTML(response.body)
        item = JdItem()
        urls = selector.xpath('//div[@class="p-name"]/a/@href')
        print(urls)
        for url in urls:
            if url.startswith('http'):
                item['info_url'] = url
                yield scrapy.Request(url=url, headers=self.header, callback=self.get_info, meta={'item': item})
            elif url.startswith('//'):
                url = 'https:' + url
                item['info_url'] = url
                yield scrapy.Request(url=url, headers=self.header, callback=self.get_info, meta={'item': item})

    def get_info(self, response):
        selector = etree.HTML(response.body)
        item = response.meta['item']
        title = selector.xpath('string(//div[@class="itemInfo-wrap"]/div[@class="sku-name"])').strip()
        introduce = selector.xpath('string(//div[@class="p-parameter"])')
        img = selector.xpath('//img[@id="spec-img"]/@data-origin')[0]
        vender_id = re.findall('venderId:(\d+)', str(response.body))[0]
        product_id = re.findall('/(\d+).html', str(response.url))[0]
        string = title + item['info_url']
        id = hashlib.md5(string.encode('utf-8')).hexdigest()
        item['_id'] = id
        item['title'] = title
        item['introduce'] = introduce
        item['img'] = img
        html = requests.get(url=self.json_url.format(product_id, vender_id) + self.tail,
                            headers=self.header).content.decode('gb2312',
                                                                'ignore')
        try:
            init = re.sub('jQuery\d+', '', html).strip('[()]')
            content = re.sub('":\w+,', '":"",', init)
            info = json.loads(content)
            item['price'] = info['stock']['jdPrice']['p']
            item['weight'] = info['stock']['weightValue']
        except Exception as err:
            item['price'] = ''
            item['weight'] = ''
            print(repr(err))
        yield item
