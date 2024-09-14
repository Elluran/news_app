import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
import requests


def get_news_from_telegram(channels, banned_topics):
    url = "http://127.0.0.1:8000/get_news/"
    data = {"channels": channels, "banned_topics": banned_topics}

    response = requests.post(url, json=data)
    return response.json()


with st.sidebar:
    st.title("News App")
    banned_topics = st_tags(label="Negative-topics:")
    channels = st_tags(
        value=["t.me/test_channel_news_123"], label="Telegram channels:"
    )


st.title("Feed")

news = get_news_from_telegram(channels, banned_topics)

for item in news["filtered_news"]:
    st.markdown(item["text"])
    st.caption("Source:  " + item["source"])
    st.divider()

st.title("Filtered out news")

for item in news["filtered_out_news"]:
    st.markdown(item["text"])
    st.caption("Source:  " + item["source"])
    st.divider()
