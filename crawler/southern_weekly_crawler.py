import os
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class InfzmCrawler:
    def __init__(self, term_ids):
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }
        self.base_url = "http://www.infzm.com/contents"

        # save path
        save_path = 'chinese_data/Southern_weekly/'
        os.makedirs(save_path, exist_ok=True)

        # multi-thread crawling
        with ThreadPoolExecutor(max_workers=5) as executor:
            for term_id in term_ids:
                executor.submit(self.download_news, term_id, save_path)

        print("Finsihed crawling Southern Weekly.")

    def fetch_url(self, url):
        """obtain HTML content from the URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return ""

    def parse_news_list(self, html):
        """parse the news list page and extract news ID, title"""
        try:
            news_data = json.loads(html)["data"]["contents"]
            for news in news_data:
                yield news["id"], news["subject"]
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing news list: {e}")

    def parse_news_content(self, html):
        """parse the news content page and extract the news content"""
        try:
            soup = BeautifulSoup(html, "html.parser")
            content_div = soup.find("div", class_="nfzm-content__content")
            blockquote = content_div.find("blockquote", class_="nfzm-bq") if content_div else None
            full_text_div = content_div.find("div", class_="nfzm-content__fulltext") if content_div else None
            paragraphs = full_text_div.find_all("p") if full_text_div else []

            content = blockquote.text + "\n" if blockquote else ""
            content += "\n".join([p.text for p in paragraphs if p.text.strip()])
            return content
        except AttributeError as e:
            print(f"Error parsing news content: {e}")
            return ""

    def save_file(self, path, filename, content):
        """save the content to the file"""
        try:
            with open(os.path.join(path, filename), 'a', encoding='utf-8') as f:
                f.write(content + "\n\n")
        except IOError as e:
            print(f"Error saving file: {e}")

    def download_news(self, term_id, save_path):
        """download news for a specific term"""
        page = 1
        filename = f"term_{term_id}.txt"
        while True:
            url = f"{self.base_url}?term_id={term_id}&page={page}&format=json"
            html = self.fetch_url(url)
            if not html.strip():
                break

            news_exist = False
            for news_id, title, publish_time in self.parse_news_list(html):
                news_exist = True
                news_url = f"{self.base_url}/{news_id}"
                news_content = self.parse_news_content(self.fetch_url(news_url))
                full_content = f"{title}\n{news_content}"
                self.save_file(save_path, filename, full_content)

            if not news_exist:
                break
            page += 1


if __name__ == "__main__":
    term_ids = [1, 2, 3, 4, 5, 6, 7]
    InfzmCrawler(term_ids)
