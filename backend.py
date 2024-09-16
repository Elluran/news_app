from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from llm_functions import text_contains_topic, shorten_text
from pymongo import MongoClient
import tomli
import os

app = FastAPI()
db_client = MongoClient(os.getenv("MONGODB_ADDRESS"))
db = db_client["news_database"]
posts_collection = db["posts"]
sources_collection = db["channels"]


def get_messages_grouped_by_source(n_messages_to_fetch, sources):
    pipeline = [
        {"$match": {"source": {"$in": sources}}},
        {"$sort": {"date": -1}},
        {
            "$group": {
                "_id": "$source",
                "messages": {
                    "$push": {
                        "id": "$_id",
                        "text": "$text",
                        "short_version": "$short_version",
                        "date": "$date",
                    }
                },
            }
        },
        {
            "$project": {
                "messages": {"$slice": ["$messages", n_messages_to_fetch]},
                "_id": 1,
            }
        },
    ]
    grouped_messages = list(posts_collection.aggregate(pipeline))
    return grouped_messages


class GetNewsBody(BaseModel):
    channels: List[str]
    banned_topics: List[str]
    short: bool = False
    news_to_fetch: int = 3


def add_source(source):
    sources_collection.update_one(
        {"_id": source},
        {"$setOnInsert": {"_id": source, "message_id": 0}},
        upsert=True,
    )


@app.post("/get_news/")
async def get_news(body: GetNewsBody):

    for channel in body.channels:
        add_source(channel)

    grouped_news = get_messages_grouped_by_source(
        body.news_to_fetch, body.channels
    )

    unfiltered_news = []
    for source in grouped_news:
        news = []
        for message in source["messages"]:
            print(message)
            if message["text"]:
                news.append(
                    {
                        "text": message["text"],
                        "source": source["_id"],
                        "date": message["date"],
                    }
                )

        unfiltered_news += news

    unfiltered_news = reversed(sorted(unfiltered_news, key=lambda x: x["date"]))

    filtered_news = []
    filtered_out_news = []
    for news in unfiltered_news:
        news["date"] = news["date"].strftime("%Y-%m-%d %H:%M")

        if text_contains_topic(body.banned_topics, news["text"]):
            filtered_out_news.append(news)
        else:
            filtered_news.append(news)

    if body.short:
        for news in filtered_news:
            news["text"] = shorten_text(news["text"])

    return {
        "filtered_news": filtered_news,
        "filtered_out_news": filtered_out_news,
    }
