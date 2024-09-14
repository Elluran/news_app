from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from llm_functions import text_contains_topic, shorten_text
from telethon import TelegramClient, events, sync
import tomli

app = FastAPI()


class Item(BaseModel):
    channels: List[str]
    banned_topics: List[str]
    short: bool = False


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
        news = []
        for message in await client.get_messages(channel, limit=2):
            if message.text != "":
                news.append({"text": message.text, "source": channel})
        
        unfiltered_news += news

    filtered_news = []
    filtered_out_news = []
    for news in unfiltered_news:
        if text_contains_topic(item.banned_topics, news["text"]):
            filtered_out_news.append(news)
        else:
            filtered_news.append(news)

    await client.disconnect()

    if item.short:
        for news in filtered_news:
            news["text"] = shorten_text(news["text"])

    return {
        "filtered_news": filtered_news,
        "filtered_out_news": filtered_out_news,
    }
