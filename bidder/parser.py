from playwright.async_api import async_playwright, Locator, Page, Browser, TimeoutError

from abc import abstractmethod, ABC

import asyncio
import os
import urllib

from .schemas import AuthPluginSchema, AuthPluginSelectors, WbSelectors
from .custom_exceptions import AlreadyAuthenticatedException
from utils.exceptions import (
    ALREADY_AUTH_PLUGIN, TIMEOUT, NOT_AVAILABLE_NEURO, DOES_NOT_EXISTS,
    BAD_DATA_TO_AUTH
)
from neuro.lineal_regression import NeuroAnalytics, DataPrepare

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

    @abstractmethod
    async def wait_time(self, page: Page, time: int) -> None:
        ...

    @abstractmethod
    async def do_js(self, page: Page, script: str) -> None:
        ...

    @abstractmethod
    async def get_text(self, locator: Locator) -> str:
        ...

    @abstractmethod
    def get_element_by_locator(
        self, 
        get_from: Page | Locator,
        selector: str
    ) -> Locator:
        ...

class PlaywrightParser(Parser):
    TIMEOUT = 10_000

    def __init__(self, user_data_dir: str, path_to_plugin: str):
        self.user_data_dir = user_data_dir
        self.path_to_plugin = os.path.expanduser(path_to_plugin)
        self.headless = False

    def __del__(self):
        os.rmdir(self.user_data_dir)

    async def get_options(self) -> dict:
        return {
            "user_data_dir": self.user_data_dir,
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

    async def wait_time(self, page: Page, time: int) -> None:
        await page.wait_for_timeout(time)

    async def do_js(self, page: Page, script: str) -> None:
        await page.evaluate(script)

    async def get_text(self, locator: Locator) -> str:
        return await locator.text_content()
    
    def get_element_by_locator(
        self, 
        get_from: Page | Locator,
        selector: str
    ) -> Locator:
        return get_from.locator(selector)

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
        except TimeoutError:
            raise ValueError(NOT_AVAILABLE_NEURO)

        await self._auth(url_to_login=login_link, url_to_back=goods_wb_url)


    async def _get_link_redirect_to_page_auth_in_plugin(self) -> str:
        tag_to_redirect_login_page = await self._get_tag_by_selector(
            selector=self.selectors.login_button
        )
        href_login_page = await self._get_attribute_from_tag(
            tag=tag_to_redirect_login_page,
            tag_name="href"
        )

        self._ensure_authentication_required(href=href_login_page)

        return href_login_page
    
    async def _auth(self, url_to_login: str, url_to_back: str) -> None:
        try:
            await self._goto_url(url=url_to_login)
            await self._auth_in_plugin()
            await self._goto_wb_back(url=url_to_back)
        except TimeoutError:
            raise ValueError(BAD_DATA_TO_AUTH)

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
    
    async def _get_attribute_from_tag(self, tag: Locator, tag_name: str) -> str:
        return await self.parser.get_attribute(
            tag=tag, 
            tag_name=tag_name
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


class WbParser:
    SCROLL_WAITING = 10_000
    SCRIPT = """
        (async function() {
            const scrollHeight = 15000;
            let scrollPosition = 0;
            const scrollStep = 50;

            while (scrollPosition < scrollHeight) {
                window.scrollTo(0, scrollPosition);
                scrollPosition += scrollStep;

                await new Promise(resolve => setTimeout(resolve, 100));
            }
        })();
    """ 
    SHOW_PAGE = 2

    def __init__(self, page: Page, parser: Parser):
        self.page = page
        self.selectors = WbSelectors()
        self.parser = parser

    async def get_data(self, url: str) -> list:
        if not await self._can_parse():
            raise ValueError(NOT_AVAILABLE_NEURO)
        
        data_parsed = []    
        for _ in range(self.SHOW_PAGE):
            await self._scrolling_page()

            data_parsed += await self._collect_data(current_url=url)
            await self._go_to_next_page()

        return data_parsed

    async def _can_parse(self) -> bool:
        try:
            await self.parser.wait_selector(page=self.page, selector=self.selectors.can_parse_data)
        except TimeoutError:
            return False
        return True

    async def _scrolling_page(self) -> None:
        await self.parser.do_js(page=self.page, script=self.SCRIPT)
        await self.parser.wait_time(page=self.page, time=self.SCROLL_WAITING)
    
    async def _go_to_next_page(self) -> None:
        next_button = await self.parser.get_element_by_selector(
            page=self.page,
            selector=self.selectors.next_page,
            index=0
        )
        await self.parser.click(element=next_button)

    async def _collect_data(self, current_url: str) -> list:
        data_to_save = []
        try:
            items = self.parser.get_element_by_locator(
                get_from=self.page,
                selector=self.selectors.goods_on_page
            )
        except:
            return data_to_save

        for item in await items.all():
            try:
                articul_wb = await self._get_articul_wb(item=item)

                marks = await self._get_marks(articul_wb=articul_wb)
                count_marks = await self._get_count_marks(articul_wb=articul_wb)
                fbo = await self._get_fbo(articul_wb=articul_wb)
                num_of_the_rating = await self._get_num_of_the_rating(
                    articul_wb=articul_wb
                )
                
                from_value = await self._get_from_value(item=item)
                price = await self._get_price(item=item)

                url = self._get_urL(url=current_url)
            except ValueError as e:
                continue

            data_to_save.append(
                (from_value, price, url, marks, count_marks, fbo, num_of_the_rating)
            )

        return data_to_save

    async def _get_articul_wb(self, item: Locator) -> str:
        return (
            await (item.get_attribute(self.selectors.wb_articul))
        ).split("-")[-1]

    async def _get_marks(self, articul_wb: str) -> str:
        return await self._get_text_content_by_selector(
            selector=self.selectors.marks,
            articul_wb=articul_wb
        )
    
    async def _get_count_marks(self, articul_wb: str) -> str:
        return await self._get_text_content_by_selector(
            selector=self.selectors.count_marks,
            articul_wb=articul_wb
        )

    async def _get_fbo(self, articul_wb: str) -> str:
        return await self._get_text_content_by_selector(
            selector=self.selectors.fbo,
            articul_wb=articul_wb
        )

    async def _get_num_of_the_rating(self, articul_wb: str) -> str:
        return await self._get_text_content_by_selector(
            selector=self.selectors.num_of_the_rating,
            articul_wb=articul_wb
        )

    async def _get_text_content_by_selector(
        self, 
        selector: str,
        articul_wb: str 
    ) -> str:
        locator =  await self.parser.get_element_by_selector(
            page=self.page,
            selector=selector.format(articul_wb=articul_wb),
            index=0
        )
        if locator:
            return await self.parser.get_text(locator=locator) 
        else:
            raise ValueError(DOES_NOT_EXISTS)

    async def _get_from_value(self, item: str) -> str:
        return await self._get_text_content_by_locator(
            item=item,
            selector=self.selectors.from_value
        )

    async def _get_price(self, item: str) -> str:
        return await self._get_text_content_by_locator(
            item=item,
            selector=self.selectors.price
        )

    async def _get_text_content_by_locator(
        self, 
        item: Locator,
        selector: str
    ) -> str:
        locator = self.parser.get_element_by_locator(
            get_from=item,
            selector=selector
        )
        if locator:
            return await self.parser.get_text(locator=locator) 
        else:
            raise ValueError(DOES_NOT_EXISTS)

    def _get_urL(self, url):
        return urllib.parse.unquote(url)

async def parse_plugin_data(url: str, user_data_dir: str, path_to_plugin: str, auth_data: AuthPluginSchema) -> None:
    '''
    Функция для проверки парсера, НЕ ИСПОЛЬЗОВАТЬ В НЕЙРОБИДДЕРЕ, ОТДЕЛЬНО СОЗДАТЬ
    в продакшине удалить
    '''
    playwright_parser = PlaywrightParser(
        user_data_dir=user_data_dir, 
        path_to_plugin=path_to_plugin
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            **(await playwright_parser.get_options())
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
            raise(e)

        wb_parser = WbParser(page=page, parser=playwright_parser)

        try:
            data = await wb_parser.get_data(url=url)
        except Exception as e:
            raise(e)

        try:
            prepare = DataPrepare(parsed_data=data)
            neuro = NeuroAnalytics(prepare=prepare)
        
            data = neuro.start()
            print(data)
        except Exception as e:
            raise(e)

def main(path_to_plugin: str, user_data_dir: str, url: str, auth_data: AuthPluginSchema):
    asyncio.run(parse_plugin_data(
        path_to_plugin=path_to_plugin,
        user_data_dir=user_data_dir,
        url=url,
        auth_data=auth_data
    ))

if __name__ == "__main__":
    plugin_path = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Extensions\eabmbhjdihhkdkkmadkeoggelbafdcdd\2.15.29_0"
    auth = AuthPluginSchema(
        login="ip-kalugina-olga-viktorovna@eggheads.solutions",
        password="JVD4Revp"
    )
    # url = "https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B0%20%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F"
    url = "https://www.wildberries.ru/catalog/0/search.aspx?search=комплект%20сигнализации"
    user_data_dir="dsadsdads123333"
    main(path_to_plugin=plugin_path, user_data_dir=user_data_dir, url=url, auth_data=auth)