import os
import requests
import logging
import time
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor

# 设置日志配置
logging.basicConfig(level=logging.DEBUG)

# Edge驱动路径
driver_path = "D:\\edge\\edgedriver_win64\\msedgedriver.exe"
class GlobalTimesCrawler:
    def __init__(self, url, columns, save_path, max_pages=10, wait_time=1):
        self.url = url
        self.columns = columns
        self.save_path = save_path
        self.max_pages = max_pages
        self.wait_time = wait_time
        driver_path = "D:\\edge\\edgedriver_win64\\msedgedriver.exe"
        self.driver = webdriver.Edge(executable_path=driver_path)
        self.driver.implicitly_wait(10)
        os.makedirs(save_path, exist_ok=True)
        
        # crawl news 
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.download_news, column) for column in self.columns]
            for future in futures:
                future.result()
        self.driver.quit()
        print("Finished crawling Global Times news")

    def fetch_url(self, url):
        """obtain HTML content from the URL"""
        try:
            self.driver.get(url)
            time.sleep(self.wait_time)
            return self.driver.page_source
        except Exception as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return ""

    def parse_news_list(self, html):
        """parse the news list page and extract news title, link"""
        try:
            html_tree = etree.HTML(html)
            articles = html_tree.xpath('//div[@class="level01_list"]//div[@class="list_info"]/a')
            for article in articles:
                title = article.xpath('./text()')[0].strip()
                link = article.xpath('./@href')[0]
                yield title, link
        except Exception as e:
            logging.error(f"Error parsing news list: {e}")

    def parse_news_content(self, html):
        """parse the news content page and extract the news content"""
        try:
            html_tree = etree.HTML(html)
            content_lst = html_tree.xpath('//div[@class="article_page"]//div[@class="article_content"]//div[@class="article_right"]/br')
            content = "\n".join([one.tail.strip() for one in content_lst if one.tail])
            return content
        except Exception as e:
            logging.error(f"Error parsing news content: {e}")
            return ""

    def save_file(self, column, title, content):
        """save the content to the file"""
        try:
            filename = os.path.join(self.save_path, f"{column}_news.txt")
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"{title}\n{content}\n\n")
        except IOError as e:
            logging.error(f"Error saving file: {e}")

    def download_news(self, column):
        """download news for a specific column"""
        logging.info(f"getting news_columns: {column}")
        page = 1
        while page <= self.max_pages:
            logging.info(f"getting {column} Page {page} ")
            url = f"{self.url}/{column}"
            html = self.fetch_url(url)
            if not html:
                break

            news_exist = False
            for title, link in self.parse_news_list(html):
                news_exist = True
                news_html = self.fetch_url(link)
                content = self.parse_news_content(news_html)
                self.save_file(column, title, content)

            if not news_exist:
                break
            page += 1
        logging.info(f"news_columns {column} finished")

if __name__ == "__main__":
    news_columns_dict = {
        # 'politics': '政治',
        # 'society': '社会',
        # 'diplomacy': '外交',
        'military': '军事',
        'science': '科学',
        'odd': '奇文',
        'graphic': '图文',
    }

    crawler = GlobalTimesCrawler(
        url='https://www.globaltimes.cn/china',
        columns=news_columns_dict,
        save_path='english_data/Global_Times_new',
        max_pages=10,
        wait_time=1
    )
