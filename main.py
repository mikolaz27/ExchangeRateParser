import re
from decimal import Decimal

import requests
from bs4 import BeautifulSoup, Tag
from requests import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class PageIsNotAccessible(Exception):
    def __init__(self, status_code: int, response: Response):
        self._status_code = status_code
        self._response = response

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def response(self) -> Response:
        return self._response


class Parser:
    def __init__(self, url: str = 'https://www.google.com/'):
        self._url = url
        self._response = None

    @property
    def url(self) -> str:
        return self._url

    def _get_page_response(self, update_cache: bool = False) -> Response:
        if self._response and not update_cache:
            return self._response

        response = requests.get(self.url)
        self._save_response_to_cache(response)
        if response.status_code >= 400:
            raise PageIsNotAccessible(status_code=self._response.status_code, response=response)
        return response

    def _save_response_to_cache(self, response: Response):
        self._response = response

    def get_page_sources(self) -> str:
        return self.get_page_soup().prettify()

    def get_page_soup(self) -> BeautifulSoup:
        raw_sources = self._get_page_response().text
        return BeautifulSoup(raw_sources, 'html.parser')

    @staticmethod
    def initiate_web_driver() -> webdriver.Firefox:
        options = Options()
        options.add_argument('--headless')
        return webdriver.Firefox(options=options)


class ExchangeRate:
    def __init__(self, raw_rate: str):
        self._raw_rate = raw_rate

    @property
    def value(self) -> Decimal:
        return Decimal(self._replace_decimal(self._raw_rate))

    @staticmethod
    def _replace_decimal(amount: str, separator: str = '.') -> str:
        return amount.replace(',', separator)

    def __str__(self) -> str:
        return f'Rate: {self.value}'


class PhoneNumber:
    def __init__(self, raw_phone: str):
        self._raw_phone = raw_phone

    @property
    def value(self) -> str:
        return re.sub(r'\s', '', self._raw_phone)

    def __str__(self) -> str:
        return self.value


class ExchangeRateBlock:
    def __init__(self, soup_element: Tag):
        self._soup_element = soup_element

    @property
    def id(self):
        return self._soup_element.attrs['id']

    @property
    def rate(self) -> ExchangeRate:
        rate, _ = self._soup_element.select_one('div.Typography').text.split()
        return ExchangeRate(rate)


class MinFinExchangeRateParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(url='https://minfin.com.ua/currency/auction/usd/buy/kiev/')

    def get_average_exchange_rate(self) -> ExchangeRate:
        soup = self.get_page_soup()
        raw_rate = soup.select_one('span.Typography').text
        rate = re.search(r'\d{2}[,.]\d{2}', raw_rate)
        return ExchangeRate(rate[0])

    def _get_all_exchange_blocks(self) -> list[ExchangeRateBlock]:
        soup = self.get_page_soup()
        soup.select('div.CardWrapper')
        return [ExchangeRateBlock(exchange_block) for exchange_block in soup.select('div.CardWrapper')]

    def _get_maximum_rate_exchange_block(self) -> ExchangeRateBlock:
        return max(
            self._get_all_exchange_blocks(),
            key=lambda exchange_rate_block: exchange_rate_block.rate.value
        )

    def get_max_exchange_rate(self) -> ExchangeRate:
        return self._get_maximum_rate_exchange_block().rate

    def get_max_exchange_rate_phone(self) -> PhoneNumber:
        block_id = self._get_maximum_rate_exchange_block().id
        driver = self.initiate_web_driver()
        driver.get(self.url)
        element = driver.find_element(By.CSS_SELECTOR, f'div[id="{block_id}"] div.phoneBlock')
        driver.execute_script("arguments[0].click();", element)
        return PhoneNumber(element.text)


if __name__ == '__main__':
    mf_parser = MinFinExchangeRateParser()
    print(mf_parser.get_average_exchange_rate())
    print(mf_parser.get_max_exchange_rate())
    print(mf_parser.get_max_exchange_rate_phone())
