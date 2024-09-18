from pymongo import MongoClient
from datetime import datetime
from telethon import TelegramClient, events, sync
import asyncio
import tomli
import time
import os
import random


client = MongoClient(os.getenv("MONGODB_ADDRESS"))

db = client["news_database"]
posts_collection = db["posts"]
sources_collection = db["channels"]


def check_message_exists(source, message_id):
    query = {"message_id": message_id, "source": source}
    message = posts_collection.find_one(query)

    return message is not None


def insert_message(text, source, short_version, date, message_id):
    if check_message_exists(source, message_id):
        return

    message = {
        "text": text,
        "source": source,
        "short_version": short_version,
        "date": date,
        "message_id": message_id,
    }

    posts_collection.insert_one(message)


def get_sources():
    sources = sources_collection.find({})
    return [(source["_id"], source["message_id"]) for source in sources]


def update_message_id(source, new_id):
    sources_collection.update_one(
        {"_id": source}, {"$set": {"_id": source, "message_id": new_id}}
    )


async def get_telegram_client():
    with open("creds.toml", "rb") as f:
        creds = tomli.load(f)

    client = TelegramClient(
        creds["telegram"]["phone_number"],
        creds["telegram"]["api_id"],
        creds["telegram"]["api_hash"],
    )
    return client


async def main():
    client = await get_telegram_client()
    await client.connect()

    channels = get_sources()

    for channel, last_id in channels:
        if last_id == 0:
            messages = await client.get_messages(channel, limit=100)
        else:
            messages = await client.get_messages(
                channel, min_id=last_id, max_id=last_id + 100
            )
        for message in messages:
            if message.text:
                insert_message(
                    message.text, channel, "", message.date, message.id
                )

        if len(messages) > 0:
            update_message_id(channel, messages[0].id)

        print(f"Added {len(messages)} new messages from {channel}", flush=True)

    await client.disconnect()


while True:
    asyncio.run(main())
    time.sleep(300 + random.randint(0, 120))
