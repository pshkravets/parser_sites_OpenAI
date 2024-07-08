import re
import cloudscraper

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from openai import OpenAI

scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
base_url = input('Введіть адресу сайту')
website_info = []
urls = set()
temporary_urls = set()
temporary_urls.add(base_url)
pages = 5
client = OpenAI(
    api_key=''
)

def is_internal_link(href, base_url):
    parsed_base_url = urlparse(base_url)
    parsed_href = urlparse(urljoin(base_url, href))
    return parsed_base_url.netloc == parsed_href.netloc


def get_full_url(url, base_url):
    if urlparse(base_url).netloc in url:
        return url
    return urlparse(base_url).scheme + '://' + urlparse(base_url).netloc + url


def process_website_info(info):
    cleaned_text = ''
    for text in info:
    # text = info[0].get_text()
        cleaned_text = cleaned_text + re.sub(r'\n+', '\n', text.get_text())
    return cleaned_text[:25000]

def summarize(*data):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", f"content": f'''На основі наданої інформації про сайт, підсумуй
         що він надає і який аудиторії {data}'''}]
    )
    print(response.choices[0].message.content)
    # print(response['message'])


while len(website_info) <= pages:
    new_urls = set()
    for url in temporary_urls:
        soup = BeautifulSoup(scraper.get(url).text, 'html.parser')
        links = soup.find_all('a', href=True)
        for a in links:
            full_url = get_full_url(a['href'], base_url)
            if is_internal_link(a['href'], base_url) and \
                    scraper.get(full_url).status_code == 200:
                new_urls.add(full_url)
            if len(urls) + len(new_urls) >= pages:
                break
        website_info += [soup.find('body')]
        if len(website_info) >= pages:
            break
    temporary_urls = new_urls
    urls.update(new_urls)

# print(website_info)
summarize(process_website_info(website_info))
# process_website_info(website_info)
# managing_info_limit(website_info)
