# 第三方插件
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# 第三方包
from lxml import etree
import redis

# 项目内置包
import time


class ProductIdSpider(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379)
        self.start_url = "https://www.jd.com/?cu=true&utm_source=baidu-pinzhuan&utm_medium=cpc&utm_campaign=t_288551095_baidupinzhuan&utm_term=0f3d30c8dba7459bb52f2eb5eba8ac7d_0_0ba6a4139a764dcfa26b16e2ecb4dd91"
        self.browser = webdriver.Chrome(
            executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')

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
                    self.r.sadd('info_url', url)
                elif url.startswith('//'):
                    url = 'https:' + url
                    self.r.sadd('info_url', url)


if __name__ == '__main__':
    spider = ProductIdSpider().start_requests()
