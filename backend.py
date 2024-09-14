from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from llm_filter import text_contains_topic
from telethon import TelegramClient, events, sync
import tomli

app = FastAPI()


class Item(BaseModel):
    channels: List[str]
    banned_topics: List[str]


async def get_telegram_client():
    with open("telegram_creds.toml", "rb") as f:
        creds = tomli.load(f)

    client = TelegramClient(
        creds["phone_number"], creds["api_id"], creds["api_hash"]
    )
    return client


@app.post("/get_news/")
async def get_news(item: Item):
    client = await get_telegram_client()
    await client.connect()

    unfiltered_news = []
    for channel in item.channels:
        news = [
            {"text": message.text, "source": channel}
            for message in await client.get_messages(channel, limit=4)
        ]
        unfiltered_news += news

    filtered_news = [
        news
        for news in unfiltered_news
        if not text_contains_topic(item.banned_topics, news["text"])
    ]

    await client.disconnect()

    return filtered_news
