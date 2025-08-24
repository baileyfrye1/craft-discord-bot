import asyncio
import logging

import httpx
from bs4 import BeautifulSoup

from discord_setup import client, start_discord

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


async def check_product_status():
    async with httpx.AsyncClient() as http_client:
        while True:
            try:
                resp = await http_client.get(
                    "https://www.craftclubco.com/products/ice-storm-moss-coaster-kit"
                )

                if resp.status_code == 404:
                    print("Page could not be loaded, skipping")
                else:
                    soup = BeautifulSoup(resp.text, "html.parser")

                    sold_out_badge = soup.find("sold-out-badge")

                    if sold_out_badge and not sold_out_badge.has_attr("hidden"):
                        print(f"{soup.title.string} is sold out, skipping")
                    else:
                        await client.send_message(
                            f"{soup.title.string} is available: \n{resp.url}"
                        )
            except Exception as e:
                logger.error(f"Error checking product: {e}")

            await asyncio.sleep(60 * 60 * 24)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(start_discord())
        tg.create_task(check_product_status())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error("Forced shutdown.")
