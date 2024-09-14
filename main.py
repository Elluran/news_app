import streamlit as st
import requests


def get_news_from_telegram(channels, banned_topics):
    url = "http://127.0.0.1:8000/get_news/"
    data = {"channels": channels, "banned_topics": banned_topics}

    response = requests.post(url, json=data)
    return response.json()

st.title("News App")
banned_topics = st.text_area(label="Negative-topics").split(";")

channels = ["t.me/test_channel_news_123"]
news_list = get_news_from_telegram(channels, banned_topics)

for item in news_list:
    st.write(item)
    st.divider()
