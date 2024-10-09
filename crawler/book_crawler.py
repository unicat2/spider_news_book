#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

DRIVER_PATH = "D:\\edge\\edgedriver_win64\\msedgedriver.exe"

class EnglishBookCrawler:
    def __init__(self, base_url, output_dir, driver_path=DRIVER_PATH):
        self.base_url = base_url
        self.output_dir = output_dir
        self.driver_path = driver_path
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def setup_webdriver(self, url):
        """Set up WebDriver to get the page"""
        logger.info(f"Starting WebDriver to get the page: {url}")
        driver = webdriver.Edge(executable_path=self.driver_path)
        driver.get(url)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
        return driver

    def save_to_txt(self, data_list, file_name):
        """Save the data to a text file"""
        output_path = os.path.join(self.output_dir, f"{file_name}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data_list:
                f.write(item['text'] + "\n")
        logger.info(f"Data successfully saved to: {output_path}")

    def fetch_book_content(self, book_url):
        """Obtain the content of a book"""
        if not book_url.endswith('read'):
            return
        book_id = book_url.split('/')[-2]
        logger.info(f"Starting to crawl book content: {book_id}")
        try:
            book_page = requests.get(self.base_url + book_url).content.decode()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch book: {book_url} - {e}")
            return

        soup = BeautifulSoup(book_page, 'lxml')
        sections = soup.find_all('div', class_=re.compile('page n.*'))
        res_list = []
        for section in sections:
            section_text = ''.join(p.text.strip() for p in section.find_all('p') if p.text.strip())
            if section_text:
                res_list.append({'text': section_text})

        self.save_to_txt(res_list, book_id)

    def crawl_books(self):
        """Crawl the list of books and call specific book crawlers"""
        root_url = self.base_url + '/en/books/en'
        driver = self.setup_webdriver(root_url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        books = soup.find_all(class_='field-content')
        book_urls = [item.a['href'] for item in books]

        logger.info(f"Found {len(book_urls)} books, starting multithreaded crawling")

        # Use thread pool to crawl book content concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.fetch_book_content, book_urls)

        logger.info("All books have been crawled")

if __name__ == "__main__":
    # Output path
    OUTPUT_DIR = './english_data/books/'

    # Instantiate the crawler class and start crawling
    crawler = EnglishBookCrawler(base_url='https://anylang.net', output_dir=OUTPUT_DIR)
    crawler.crawl_books()
