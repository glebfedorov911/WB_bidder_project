from playwright.async_api import async_playwright, Locator, Page, Browser, TimeoutError

from abc import abstractmethod, ABC

import asyncio
import os
import urllib


class Parser(ABC):

    @abstractmethod
    async def click(self, element: Locator) -> None:
        ...
    
    @abstractmethod
    async def fill(self, element: Locator, value_to_fill: str) -> None:
        ...

    @abstractmethod
    async def get_element_by_selector(self, selector: str, index: int | None = None) -> Locator:
        ...

class IPlaywrightParser(Parser):

    @abstractmethod
    async def get_options(self, user_data_dir: str) -> dict:
        ...

    @abstractmethod
    async def goto(self, page: Page, url: str) -> None:
        ...

    @abstractmethod
    async def new_page(self, browser: Browser) -> Page:
        ...

    @abstractmethod
    async def close_browser(self, browser: Browser) -> None:
        ...
    
    @abstractmethod
    async def get_attribute(self, tag: Locator, tag_name: str) -> str:
        ...

    @abstractmethod
    async def wait_selector(self, page: Page, selector: str) -> bool:
        ...

class PlaywrightParser(IPlaywrightParser):
    TIMEOUT = 10_000

    def __init__(self, path_to_plugin: str):
        self.path_to_plugin = os.path.expanduser(path_to_plugin)
        self.headless = False

    async def get_options(self, user_data_dir: str) -> dict:
        return {
            "user_data_dir": user_data_dir,
            "args": [
                f"--disable-extensions-except={self.path_to_plugin}",
                f"--load-extension={self.path_to_plugin}",
            ],
            "headless": self.headless
        }

    async def goto(self, page: Page, url: str) -> None:
        await page.goto(url)

    async def new_page(self, browser: Browser) -> Page:
        return await browser.new_page()

    async def close_browser(self, browser: Browser) -> None:
        await browser.close()

    async def fill(self, element: Locator, value_to_fill: str) -> None:
        await element.fill(value_to_fill)

    async def click(self, element: Locator) -> None:
        await element.click()

    async def get_attribute(self, tag: Locator, tag_name: str) -> str:
        return await tag.get_attribute(tag_name)

    async def get_element_by_selector(self, page: Page, selector: str, index: int | None = None) -> Locator:
        await self.wait_selector(page=page, selector=selector)
        elements = await page.query_selector_all(selector)
        if index is not None:
            return elements[index]
        return elements

    async def wait_selector(self, page: Page, selector: str) -> bool:
        try:
            await page.wait_for_selector(selector, timeout=self.TIMEOUT)
            return True
        except:
            raise TimeoutError("Timeout waiting")

async def login_plugin(url: str, page: Page, playwright_parser: PlaywrightParser, login: str, password: str) -> None:
    tag_to_redirect_login_page = await playwright_parser.get_element_by_selector(page=page, selector=".button-link.qa-product-widget-button-go-to-analytics", index=0)
    href_to_login_page = await playwright_parser.get_attribute(tag=tag_to_redirect_login_page, tag_name="href")
    if "login" in href_to_login_page:
        await playwright_parser.goto(page=page, url=href_to_login_page)

        login_tag = await playwright_parser.get_element_by_selector(page=page, selector=".authorization-input", index=0)
        password_tag = await playwright_parser.get_element_by_selector(page=page, selector=".authorization-input.qa-password", index=0)

        await playwright_parser.fill(element=login_tag, value_to_fill=login)
        await playwright_parser.fill(element=password_tag, value_to_fill=password)

        button_to_auth = await playwright_parser.get_element_by_selector(page=page, selector=".btn.btn-md.btn-secondary.authorization-button.qa-button-login", index=0)
        await playwright_parser.click(element=button_to_auth)

        await playwright_parser.wait_selector(page=page, selector="#mmodalpublic___BV_modal_title_")

        await playwright_parser.goto(page=page, url=url)

async def parse_plugin_data(url: str, user_data_dir: str, plugin_path: str, login: str, password: str) -> None:
    playwright_parser = PlaywrightParser(path_to_plugin=plugin_path)

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            **(await playwright_parser.get_options(user_data_dir=user_data_dir))
        )
        page = await playwright_parser.new_page(browser=browser)
        await playwright_parser.goto(page=page, url=url)
        
        try:
            await login_plugin(url=url, page=page, playwright_parser=playwright_parser, login=login, password=password)
        except TimeoutError:
            print("Проверка, уже авторизован")

        async def collect_data(page, data_to_save, current_url):
            items = page.locator(".cpm-card-widget.eggheads-bootstrap")
            i = await items.all()
            for item in await items.all():
                articul_wb = (await (item.get_attribute("id"))).split("-")[-1]
                marks = await (await page.query_selector(f"#{articul_wb} > div.product-card__wrapper > div.product-card__bottom-wrap > p.product-card__rating-wrap > span.address-rate-mini.address-rate-mini--sm")).text_content()
                count_marks = await (await page.query_selector(f"#{articul_wb} > div.product-card__wrapper > div.product-card__bottom-wrap > p.product-card__rating-wrap > span.product-card__count")).text_content()
                fbo = await (await  page.query_selector(f"#{articul_wb} > div.product-card__wrapper > div.list-widget.eggheads-product-list-widget.eggheads-bootstrap > div.b-overlay-wrap.position-relative.eggheads-overlay > ul > li:nth-child(2) > span.text.-bold")).text_content()
                num_of_the_rating = await (await page.query_selector(f"#{articul_wb} > div.product-card__wrapper > div.list-widget.eggheads-product-list-widget.eggheads-bootstrap > div.list-widget__number")).text_content()
                from_value = await (item.locator("div > div > span > span")).text_content()
                price = await (item.locator(".title")).text_content()
                url = urllib.parse.unquote(current_url)
                data_to_save.append((from_value, price, url, marks, count_marks, fbo, num_of_the_rating))

        try:
            await playwright_parser.wait_selector(page=page, selector=".cpm-card-widget.eggheads-bootstrap")
        except:
            print("Недоступно в плагине, не можем парсить")
        else:
            data_to_save = []
            await collect_data(page=page, data_to_save=data_to_save, current_url=url)

            print(data_to_save) #TODO: ДОБАВИТЬ БД ДЛЯ НЕЙРОНКИ!!!! И НАСТРОИТЬ НЕЙРОНКУ

        print("Проверка, финал")
        os.rmdir(user_data_dir)

def main(url: str, user_data_dir: str, plugin_path: str, login: str, password: str):
    asyncio.run(parse_plugin_data(url, user_data_dir, plugin_path, login, password))

if __name__ == "__main__":
    main(
# https://www.wildberries.ru/catalog/0/search.aspx?search=комплект%20сигнализации
        url="https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B0%20%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F",
        user_data_dir="dsadsdads",
        plugin_path=r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Extensions\eabmbhjdihhkdkkmadkeoggelbafdcdd\2.15.27_0",
        login="ip-kalugina-olga-viktorovna@eggheads.solutions",
        password="JVD4Revp"
    )