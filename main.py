import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os

YARDI_URL = "https://www.yardimatrix.com/Login"
TARGET_URL = "https://www.yardimatrix.com/PropertySearch"  # or wherever you're scraping

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="storage/state.json" if os.path.exists("storage/state.json") else None)
        page = await context.new_page()

        if not os.path.exists("storage/state.json"):
            await page.goto(YARDI_URL)
            print("🚪 Login manually, then press Enter here...")
            input()
            await context.storage_state(path="storage/state.json")
            print("✅ Session saved. Restart script to scrape automatically.")
            await browser.close()
            return

        print("🔐 Logged in via saved session")

        await page.goto(TARGET_URL)
        await page.wait_for_selector(".resultRow")  # <-- update this for real selector

        rows = await page.query_selector_all(".resultRow")

        data = []
        for row in rows:
            name = await row.query_selector_eval(".propertyName", "el => el.innerText") if await row.query_selector(".propertyName") else None
            address = await row.query_selector_eval(".propertyAddress", "el => el.innerText") if await row.query_selector(".propertyAddress") else None
            units = await row.query_selector_eval(".unitCount", "el => el.innerText") if await row.query_selector(".unitCount") else None
            owner = await row.query_selector_eval(".ownerName", "el => el.innerText") if await row.query_selector(".ownerName") else None
            data.append({
                "Name": name,
                "Address": address,
                "Units": units,
                "Owner": owner
            })

        df = pd.DataFrame(data)
        df.to_excel("exports/yardi_data.xlsx", index=False)
        print("📦 Data exported to exports/yardi_data.xlsx")

        await browser.close()

asyncio.run(run())
