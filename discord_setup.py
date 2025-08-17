import asyncio
import logging
import os

import discord

discord_token = os.getenv("DISCORD_TOKEN")
channel_id = os.getenv("DISCORD_CHANNEL_ID")

ready_event = asyncio.Event()

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.channel = None

    async def on_ready(self):
        logger.info(f"We are ready to start, {self.user}")

        if channel_id is not None:
            self.channel = self.get_channel(int(channel_id))
            if self.channel is None:
                logger.error(f"Failed to find channel with id: {channel_id}")
            else:
                logger.info("Ready to send messages")

            ready_event.set()
        else:
            logger.error("Channel id not provided")

    async def send_message(self, text: str):
        await ready_event.wait()
        if self.channel:
            await self.channel.send(text)
        else:
            logger.error("Channel not found")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

client = DiscordClient(intents=intents)


async def start_discord():
    if discord_token is not None:
        for i in range(0, 6):
            try:
                await client.start(discord_token)
                break
            except Exception as e:
                logger.warning(f"Discord client start failed (attempt {i + 1}): {e}")
                await asyncio.sleep(2**i)
    else:
        logger.error("Discord token not provided")
