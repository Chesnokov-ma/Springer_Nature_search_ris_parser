import os
import requests
from bs4 import BeautifulSoup
from itertools import combinations
from urllib.request import urlretrieve
from time import sleep


file_num = 0    # global file name counter


# https://stackoverflow.com/questions/464864/how-to-get-all-possible-combinations-of-a-list-s-elements
'''Word combinations from tuple/list'''
def key_words_combinations(elements: [list, tuple], L: [int]) -> tuple:
    return tuple(combinations(elements, L))


'''Change query with key words combinations and page numbers'''
class SpringNaturSearchURLGenerator:
    def __init__(self, base_search_url: [str, None] = None):
        self.__base_search_url = base_search_url

    '''New url`s generator'''
    def get_url_list(self, key_words: [list, tuple], first_page: [int] = 1, last_page: [int] = 20) -> list:
        for words in key_words:
            query = self.__change_query_string(words)
            for new_url in self.__change_page_num():
                yield new_url.replace('%%%%%', query)

    '''Change query with keywords'''
    def __change_query_string(self, key_words: [list, tuple]) -> tuple:
        return '%2C '.join(key_words).replace(' ', '+')

    '''Change page number from [first_page] to [last_page]'''
    def __change_page_num(self, first: [int] = 1, last: [int] = 200) -> str:
        for curr_page in range(first, last):
            yield self.__base_search_url.replace('!!!!!', str(curr_page))

    '''Get base url'''
    @property
    def base_search_url(self):
        return self.__base_search_url

    '''Set new base url'''
    @base_search_url.setter
    def base_search_url(self, url: [str, None]):
        self.__base_search_url = url


'''Springer Link website parser'''
class SpringerNatureRISparser:
    def __init__(self, save_folder: [str], proxies: [dict, None] = None):
        self.__proxies = proxies
        self.save_folder = save_folder

    '''Parse search webpage with url and collect .ris files in save_folder'''
    def parse(self, url: [str, None]):
        global file_num

        if self.__proxies:
            html = requests.get(url=url, proxies=self.__proxies)        # search page
        else:
            html = requests.get(url=url)

        soup = BeautifulSoup(html.content, 'html.parser')               # parse
        articles = soup.find_all("a", {"class": "title"})               # get every article on page
        for article in articles:
            href = f'http://link.springer.com{article.attrs["href"]}'
            if self.__proxies:
                article_page = BeautifulSoup(requests.get(url=href, proxies=self.__proxies).content, 'html.parser')
            else:
                article_page = BeautifulSoup(requests.get(url=href).content, 'html.parser')

            download_link = (article_page.find_all('a', {'data-test': 'citation-link',          # find download link
                                                        'data-track-action': 'download article citation'}))[0].attrs['href']

            urlretrieve(download_link, f'{self.save_folder}file{file_num}.ris')                 # download file
            file_num += 1


key_words = ['Human microbiome', 'Body Mass Index', 'obesity', 'body bioimpedance', 'Gut Microbiota']
kw_comb = key_words_combinations(key_words, 2)

search_url = 'https://link.springer.com/search/page/!!!!!?date-facet-mode=between&facet-end-year=2022&previous-end-year=2022&previous-start-year=2002&query=%%%%%&facet-content-type="Article"&facet-start-year=2002'
# proxies = {
#   "http": "http://127.0.0.1:1087",
#   "https": "http://127.0.0.1:1087",
# }

url_gen = SpringNaturSearchURLGenerator(search_url)                     # class to generate urls with key words combination
SP_parser = SpringerNatureRISparser(save_folder='tmp/')                 # Spring Nature parser

for url in url_gen.get_url_list(kw_comb, 1, 200):       # for each url -> download .ris files
    try:
        SP_parser.parse(url=url)
        print(url)
        sleep(5)
    except:
        print(f'Page {url} not found/Other error')
        continue


