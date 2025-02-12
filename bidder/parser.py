from playwright.async_api import async_playwright, Locator, Page, Browser, TimeoutError

from abc import abstractmethod, ABC

import asyncio
import os
import urllib

from .schemas import AuthPluginSchema, AuthPluginSelectors
from .custom_exceptions import AlreadyAuthenticatedException
from utils.exceptions import ALREADY_AUTH_PLUGIN, TIMEOUT


class Parser(ABC):

    @abstractmethod
    async def click(self, element: Locator) -> None:
        ...
    
    @abstractmethod
    async def fill(self, element: Locator, value_to_fill: str) -> None:
        ...

    @abstractmethod
    async def get_element_by_selector(self, page: Page, selector: str, index: int | None = None) -> Locator:
        ...

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

class PlaywrightParser(Parser):
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
        return self._get_with_index(elements=elements, index=index)

    def _get_with_index(self, elements: list[Locator], index: int | None = None):
        return elements[index] if index is not None else elements

    async def wait_selector(self, page: Page, selector: str) -> None:
        try:
            await page.wait_for_selector(selector, timeout=self.TIMEOUT)
        except:
            raise TimeoutError(TIMEOUT)
    
class PluginAuth:
    def __init__(self, page: Page, parser: Parser, auth_data: AuthPluginSchema):
        self.page = page
        self.parser = parser
        self.login = auth_data.login
        self.password = auth_data.password

        self.selectors = AuthPluginSelectors()

    async def auth_in_plugin(self, goods_wb_url: str) -> None:
        try:
            login_link = await self._get_link_redirect_to_page_auth_in_plugin()
        except AlreadyAuthenticatedException:
            print("Пользователь уже авторизован")
            return

        await self._auth(url_to_login=login_link, url_to_back=goods_wb_url)


    async def _get_link_redirect_to_page_auth_in_plugin(self) -> str:
        tag_to_redirect_login_page = await self._get_tag_by_selector(
            selector=self.selectors.login_button
        )
        href_login_page = await self._get_attribute_from_tag(
            tag=tag_to_redirect_login_page
        )

        self._ensure_authentication_required(href=href_login_page)

        return href_login_page
    
    async def _auth(self, url_to_login: str, url_to_back: str) -> None:
        try:
            await self._goto_url(url=url_to_login)
            await self._auth_in_plugin()
            await self._goto_wb_back(url=url_to_back)
        except TimeoutError:
            raise ValueError("Неправильные данные авторизации")

    async def _goto_url(self, url: str) -> None:
        await self._redirect(url=url)

    async def _auth_in_plugin(self) -> None:
        await self._input_login_data()
        await self._input_password_data()

        await self._click_button_for_auth()

    async def _input_login_data(self) -> None:
        await self._input_auth_data_to_auth_field(
            selector=self.selectors.login_field_auth, 
            value_to_fill=self.login
        )

    async def _input_password_data(self) -> None:
        await self._input_auth_data_to_auth_field(
            selector=self.selectors.password_field_auth,
            value_to_fill=self.password
        )

    async def _click_button_for_auth(self) -> None:
        tag_button_auth = await self._get_tag_by_selector(
            selector=self.selectors.auth_button
        )
        await self._button_click(tag=tag_button_auth)

    async def _goto_wb_back(self, url: str) -> None:
        tag_good_auth = await self._get_tag_by_selector(
            selector=self.selectors.good_auth
        )
        await self._check_good_auth(tag=tag_good_auth, url=url)


    async def _get_tag_by_selector(self, selector: str) -> Locator:
        return await self.parser.get_element_by_selector(
            page=self.page, 
            selector=selector, 
            index=0
        )
    
    async def _get_attribute_from_tag(self, tag: Locator) -> str:
        return await self.parser.get_attribute(
            tag=tag, 
            tag_name="href"
        )

    def _ensure_authentication_required(self, href: str | None) -> None:
        if not self._has_login_href_in_page(href=href):
            raise AlreadyAuthenticatedException(ALREADY_AUTH_PLUGIN)

    def _has_login_href_in_page(self, href: str | None) -> bool:
        return href and "login" in href.lower()

    async def _fill_value_in_tag(self, tag: Locator, value: str) -> None:
        await self.parser.fill(element=tag, value_to_fill=value)

    async def _redirect(self, url: str) -> None:
        await self.parser.goto(
            page=self.page,
            url=url
        )

    async def _input_auth_data_to_auth_field(self, selector: str, value_to_fill: str) -> None:
        auth_field = await self._get_tag_by_selector(selector=selector)
        await self._fill_value_in_tag(tag=auth_field, value=value_to_fill)

    async def _button_click(self, tag: Locator) -> None:
        await self.parser.click(element=tag)

    async def _check_good_auth(self, tag: Locator | None, url: str):
        if tag:
            await self._redirect(url=url)


async def parse_plugin_data(url: str, user_data_dir: str, path_to_plugin: str, auth_data: AuthPluginSchema) -> None:
    '''
    Функция для проверки парсера, НЕ ИСПОЛЬЗОВАТЬ В НЕЙРОБИДДЕРЕ, ОТДЕЛЬНО СОЗДАТЬ
    в продакшине удалить
    '''
    playwright_parser = PlaywrightParser(path_to_plugin=path_to_plugin)

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            **(await playwright_parser.get_options(user_data_dir=user_data_dir))
        )
        page = await playwright_parser.new_page(browser=browser)
        await playwright_parser.goto(page=page, url=url)
        
        plugin_authenticator = PluginAuth(
            page=page, 
            parser=playwright_parser,
            auth_data=auth_data
        )
        try:
            await plugin_authenticator.auth_in_plugin(goods_wb_url=url)
        except Exception as e:
            print(e)

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
            await page.evaluate("""
                (async function() {
                    const scrollHeight = 15000;
                    let scrollPosition = 0;
                    const scrollStep = 50;  // Шаг прокрутки (пиксели)

                    while (scrollPosition < scrollHeight) {
                        window.scrollTo(0, scrollPosition);
                        scrollPosition += scrollStep;

                        // Ожидаем перед следующим шагом (100ms)
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                })();
            """)
            await page.wait_for_timeout(10000)
            await collect_data(page=page, data_to_save=data_to_save, current_url=url)
            print(len(data_to_save)) 
            #TODO: ДОБАВИТЬ БД ДЛЯ НЕЙРОНКИ!!!! И НАСТРОИТЬ НЕЙРОНКУ
            #TODO: ПРОВЕРКА ДВУХ СТРАНИЦ, ЧТОБЫ ВЗЯТЬ 200 СТРОК С ДАННЫМИ
            # 1) класс для парсинга данных со страниц
            # 2) класс для сохранения этих самых данных в sqlite
            # 3) класс для нейронки 

        print("Проверка, финал")
        os.rmdir(user_data_dir)

def main(path_to_plugin: str, user_data_dir: str, url: str, auth_data: AuthPluginSchema):
    asyncio.run(parse_plugin_data(
        path_to_plugin=path_to_plugin,
        user_data_dir=user_data_dir,
        url=url,
        auth_data=auth_data
    ))

if __name__ == "__main__":
    plugin_path = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Extensions\eabmbhjdihhkdkkmadkeoggelbafdcdd\2.15.27_0"
    auth = AuthPluginSchema(
        login="ip-kalugina-olga-viktorovna@eggheads.solutions",
        password="JVD4Revp"
    )
    # https://www.wildberries.ru/catalog/0/search.aspx?search=комплект%20сигнализации
    url = "https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B0%20%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F"
    user_data_dir="dsadsdads1233"
    main(path_to_plugin=plugin_path, user_data_dir=user_data_dir, url=url, auth_data=auth)