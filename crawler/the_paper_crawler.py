#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Set the path for the browser driver
DRIVER_PATH = "D:\\edge\\edgedriver_win64\\msedgedriver.exe"

class ThePaperCrawler:
    """Class for crawling news articles from ThePaper"""

    def __init__(self, driver_path, output_dir):
        self.driver_path = driver_path
        self.output_dir = output_dir
        self.driver = webdriver.Edge(executable_path=self.driver_path)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def setup_driver(self, url):
        """Initialize the WebDriver and load the specified page"""
        logger.info(f"Starting WebDriver to get the page: {url}")
        self.driver.get(url)
        time.sleep(5)  # Increase page load time

    def scroll_to_bottom(self):
        """Simulate scrolling to the bottom of the page"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Increase wait time to ensure the page is fully loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def fetch_article_list(self):
        """Get article titles and links"""
        logger.info("Fetching article list")
        x_path = "//div[@class='news_li']/h2/a"  # Check and update XPath
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, x_path)))  # Wait for element to load
            articles = self.driver.find_elements(By.XPATH, x_path)
            article_data = [(article.text, article.get_attribute("href")) for article in articles]
            logger.info(f"Found a total of {len(article_data)} articles")
            return article_data
        except TimeoutException:
            logger.error("Timeout while fetching article list; element not found. Please check XPath or page loading status.")
            return []
        except Exception as e:
            logger.error(f"Error occurred while fetching article list: {e}")
            return []

    def fetch_article_content(self, article_title, article_url):
        """Crawl the content of a single article"""
        logger.info(f"Starting to crawl article: {article_title}")
        self.driver.get(article_url)
        try:
            x_path_title = "//main/div[4]/div[1]/div[1]/div/h1"
            title = self.driver.find_element(By.XPATH, x_path_title).text

            x_path_content = "//main/div[4]/div[1]/div[1]/div/div[2]"
            article_content = self.driver.find_element(By.XPATH, x_path_content).text
        except Exception as e:
            logger.error(f"Failed to crawl article: {article_title} - {e}")
            return article_title, None
        return title, article_content

    def save_to_txt(self, title, content):
        """Save article content to a txt file"""
        file_path = os.path.join(self.output_dir, f"{title[:50]}.txt")  # Prevent filename from being too long
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(title + "\n" + content)
        logger.info(f"Article saved to: {file_path}")

    def crawl(self):
        """Crawling process"""
        self.setup_driver("https://www.thepaper.cn/")  # Directly go to the homepage or specified page
        self.scroll_to_bottom()  # Simulate scrolling to load more content
        article_list = self.fetch_article_list()

        # Use multithreading to crawl article content
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.fetch_article_content, title, href) for title, href in article_list]
            article_contents = [f.result() for f in futures]

        # Save article content as txt
        for title, content in article_contents:
            if content:
                self.save_to_txt(title, content)


if __name__ == '__main__':
    OUTPUT_DIR = './chinese_data/Thepaper/'
    crawler = ThePaperCrawler(driver_path=DRIVER_PATH, output_dir=OUTPUT_DIR)
    crawler.crawl()
