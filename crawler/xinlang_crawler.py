import os
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import logging


class SinaCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        self.base_url = "http://news.sina.com.cn/society/"
        self.save_path = 'chinese_data/sina/'
        os.makedirs(self.save_path, exist_ok=True)

        # Use a thread pool for concurrent crawling
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.submit(self.download_news_list)

        logging.info("Finished crawling Sina news.")

    def fetch_url(self, url):
        """Fetch the HTML content of the specified URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching URL: {e}")
            return ""

    def parse_news_list(self, html):
        """Parse the news list page and extract news titles and URLs"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            for tag in soup.find('ul', class_='seo_data_list').find_all('li'):
                if tag.a:
                    yield tag.a.string, tag.a.get('href')
        except AttributeError as e:
            logging.error(f"Error parsing news list: {e}")

    def parse_news_content(self, html):
        """Parse the news content page and extract the main text and other information"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            article_tag = soup.find('div', class_='article')

            if not article_tag:
                logging.warning("No article content found.")
                return None, None

            # Get article publication date and source
            fb_date = soup.find('div', 'date-source').span.string if soup.find('div', 'date-source') else "Unknown Date"
            fb_www = soup.find('div', 'date-source').a.string if soup.find('div', 'date-source') else "Unknown Source"
            return fb_date, fb_www, article_tag.get_text()
        except AttributeError as e:
            logging.error(f"Error parsing news content: {e}")
            return None, None

    def save_file(self, filename, content):
        """Save news content to a file"""
        try:
            with open(os.path.join(self.save_path, filename), 'a', encoding='utf-8') as f:
                f.write(content + "\n\n")
        except IOError as e:
            logging.error(f"Error saving file: {e}")

    def clean_title(self, title):
        """Clean special characters from the title"""
        title = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+<>?、~*（）]+", '', title)
        return title.replace(':', '：')

    def download_news_list(self):
        """Download all news content from the news list page"""
        html = self.fetch_url(self.base_url)
        for title, url in self.parse_news_list(html):
            cleaned_title = self.clean_title(title)
            self.download_news_content(cleaned_title, url)

    def download_news_content(self, title, url):
        """Download the content of a single news article and save it"""
        html = self.fetch_url(url)
        fb_date, fb_www, content = self.parse_news_content(html)

        if content:
            filename = f"{title}.txt"
            full_content = f"{fb_date} {fb_www}\nURL: {url}\nTitle: {title}\n\n{content}"
            self.save_file(filename, full_content)
            logging.info(f"Successfully saved news: {title}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    SinaCrawler()
