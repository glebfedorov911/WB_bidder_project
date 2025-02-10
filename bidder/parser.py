from playwright.async_api import async_playwright

import asyncio
import os


class ParserAuth:

    async def auth(self, page):
        await page.wait_for_selector("#__nuxt > main > div > div > div.left > div.forms-block > div.page-variants > div.form-selector > p:nth-child(1) > a")

        a = await page.query_selector("#__nuxt > main > div > div > div.left > div.forms-block > div.page-variants > div.form-selector > p:nth-child(1) > a")
        await a.click()

        await page.wait_for_selector("#js-authorization-login")

        login = await page.query_selector("#js-authorization-login")
        password = await page.query_selector("#js-authorization-password")

        await login.fill("ip-kalugina-olga-viktorovna@eggheads.solutions")
        await password.fill("JVD4Revp")

        btn_to = await page.query_selector(".btn.btn-md.btn-secondary.authorization-button.qa-button-login")
        await btn_to.click()
            

class Parser:
    
    async def parsing(self, ):
        plugin_path = os.path.expanduser(
            r"C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Extensions\eabmbhjdihhkdkkmadkeoggelbafdcdd\2.15.27_0"
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir='user_data_dir',
                args=[
                    f"--disable-extensions-except={plugin_path}",
                    f"--load-extension={plugin_path}",
                ],  
                headless=False
            )
            page = await browser.new_page()

            await page.goto("https://www.wildberries.ru/catalog/0/search.aspx?search=комплект%20сигнализации")

            p = ParserAuth()
            await p.auth(page=page)

            await asyncio.sleep(5555)

            await browser.close()

def main():
    asyncio.run(Parser().parsing())

if __name__ == "__main__":
    main()