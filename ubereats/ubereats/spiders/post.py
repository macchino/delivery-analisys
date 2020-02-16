import scrapy
import re

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..items.shop import ShopItem
from ..constants.shop import BASE_URL, BASE_DOMAIN  # noqa


class PostSpider(scrapy.Spider):
    name = 'post'
    allowed_domains = [BASE_DOMAIN]

    def __init__(self, url="", *args, **kwargs):
        super(PostSpider, self).__init__(*args, **kwargs)

        self.target_url = url
        self.start_urls = [self.target_url]

        options = ChromeOptions()

        options.add_argument("--headless")
        options.add_argument("start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")

        self.driver = Chrome(options=options)

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.parse_shop)

    def parse_shop(self, response):
        shop = ShopItem()

        shop["name"] = response.css("h1::text").get().strip()
        point = response.css("span::text")[0].get().strip()

        if point != '•':
            shop["point"] = float(
                point.split('5 つ星のうち')[1].split(' の評価を獲得')[0].strip())
            shop["reviews"] = int(
                point.split('の評価を獲得')[1].split('件の評価に基づいています')[0].strip())

        address_info = response.css("p::text")[-1].get().strip()
        postal_code_pattern = "[0-9]{3}-?[0-9]{4}"

        postal_code = re.findall(postal_code_pattern, address_info)
        if len(postal_code) != 0:
            shop["postal_code"] = postal_code[0]

        shop["address"] = re.sub(postal_code_pattern, "",
                                 address_info).replace(",", "").strip()

        shop["url"] = response.url.strip().split("?promo=")[0]
        shop["id"] = shop["url"].split("/")[-2]
        detail_url = BASE_URL + response.xpath("//p/a/@href").get()

        request = scrapy.Request(detail_url, callback=self.parse_shop_detail)
        request.meta['shop'] = shop
        yield request

    def parse_shop_detail(self, response):
        shop = response.meta['shop']

        for _ in range(3):  # 最大3回実行
            try:
                self.driver.get(response.url)
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//figure/img")))
                res = response.replace(body=self.driver.page_source)
            except TimeoutException:
                pass
            else:
                break  # 失敗しなかった時はループを抜ける
        else:
            raise (TimeoutException())  # リトライが全部失敗した時の処理

        map_url = [
            s for s in res.css("img").xpath("@src").getall()
            if "maps.googleapis.com" in s
        ][0]
        map_info = map_url.split("center=")[1].split("&zoom=")[0].split("%2C")

        shop["latitude"] = map_info[0]
        shop["longitude"] = map_info[1]

        hour_list = [
            s for s in res.css("tbody>tr>td::text").getall() if ":" in s
        ]

        shop["open_hour"] = hour_list[0]
        shop["close_hour"] = hour_list[-1]

        yield shop

    def closed(self, reason):
        self.driver.close()
