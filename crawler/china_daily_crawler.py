import requests
from bs4 import BeautifulSoup
import re
import os
import datetime
from concurrent.futures import ThreadPoolExecutor

class ChinaDailyCrawler:
    def __init__(self, start_year, end_year):
        # base URL
        self.base_url = "http://www.chinadaily.com.cn/cndy/"
        self.start_year = start_year
        self.end_year = end_year
        
        # save path
        os.makedirs("./english_data/China_Daily/", exist_ok=True)

        # multi-thread crawling
        with ThreadPoolExecutor(max_workers=5) as executor:
            for year in range(self.start_year, self.end_year + 1):
                executor.submit(self.crawl_year, year)

    def crawl_year(self, year):

        """crawl news for a specific year"""

        print(f"Begin process year: {year}")
        news_url_list = []
        file_path = f"./english_data/China_Daily/{year}.txt"

        # start and end date of the year
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        delta = datetime.timedelta(days=1)
        current_date = start_date

        while current_date <= end_date:
            formatted_date = current_date.strftime("%Y-%m/%d/")
            index_url = f"{self.base_url}{formatted_date}index1.html"
            print(f"Fetching news for date: {current_date}")

            # obtain news URL list
            self.get_news_url_list(index_url, formatted_date, news_url_list)

            # obtain news content
            for news_url in news_url_list:
                news_text = self.get_text(news_url)
                if news_text.strip():
                    self.save_text(file_path, news_text)

            current_date += delta

        print(f"Finished year: {year}")

    def get_news_url_list(self, root_url, date_path, news_url_list):

        """obtain news URL list from the index page"""

        try:
            response = requests.get(root_url)
            response.encoding = 'utf-8'
            html = response.text

            # extract news links using regular expression
            news_links = re.findall(r"content_.*?\.htm", html)
            for link in news_links:
                full_url = f"{self.base_url}{date_path}{link}"
                news_url_list.append(full_url)
                print(f"Found news URL: {full_url}")
        except requests.RequestException as e:
            print(f"Error fetching URL list: {e}")

    def get_text(self, news_url):

        """obtain news content from the news page"""

        try:
            response = requests.get(news_url)
            response.encoding = 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            title = soup.select_one('.lft_art > h1').get_text() if soup.select_one('.lft_art > h1') else ""
            content = soup.select_one('#Content').get_text() if soup.select_one('#Content') else ""

            return f"{title}\n\n{content}" if title or content else ""
        except requests.RequestException as e:
            print(f"Error fetching text from {news_url}: {e}")
            return ""

    def save_text(self, file_path, text):

        """save news content to a file"""

        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(text + "\n\n")
            print(f"Content saved to {file_path}")
        except IOError as e:
            print(f"Error saving text: {e}")


if __name__ == "__main__":
    start_year = 2015
    end_year = 2024
    ChinaDailyCrawler(start_year, end_year)
