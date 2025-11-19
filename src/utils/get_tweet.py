import asyncio
import random
import time
from playwright.async_api import async_playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

async def human_wait(a=0.2, b=1.2):
    await asyncio.sleep(random.uniform(a, b))

async def human_mouse(page):
    """Simula un movimiento del mouse para parecer humano."""
    for _ in range(random.randint(2, 7)):
        x = random.randint(0, 1200)
        y = random.randint(0, 800)
        await page.mouse.move(x, y, steps=random.randint(5, 20))
        await human_wait(0.05, 0.3)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # muy importante — evita ser bloqueado
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
            ]
        )

        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": random.randint(1200, 1400), "height": random.randint(700, 900)},
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"longitude": -73.935242, "latitude": 40.730610},
            permissions=["geolocation"],
        )

        page = await context.new_page()

        # Quitar navigator.webdriver = True
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { 
                get: () => [1, 2, 3, 4] 
            });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            """
        )

        print("[INFO] Opening X...")
        await page.goto("https://x.com/explore", timeout=60000)
        await human_wait()

        # Simular comportamiento humano
        await human_mouse(page)
        await human_wait(1, 2)

        # Scroll humano
        for _ in range(random.randint(3, 10)):
            await page.mouse.wheel(0, random.randint(200, 600))
            await human_wait(0.3, 1.1)

        print("[INFO] Page loaded with human-like behavior.")
        await human_wait(4, 7)

        # screenshot opcional
        await page.screenshot(path="x_screenshot.png")

        await browser.close()

asyncio.run(run())
