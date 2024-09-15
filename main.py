import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
import requests


def get_news_from_telegram(
    channels, banned_topics, news_to_fetch=3, short=False
):
    url = "http://127.0.0.1:8000/get_news/"
    data = {
        "channels": channels,
        "banned_topics": banned_topics,
        "short": short,
        "news_to_fetch": news_to_fetch,
    }

    response = requests.post(url, json=data)
    return response.json()


with st.sidebar:
    st.title("News App")
    banned_topics = st_tags(label="Negative-topics:")
    channels = st_tags(
        value=["t.me/test_channel_news_123"], label="Telegram channels:"
    )
    news_to_fetch = int(
        st.number_input("news to fetch from each channel", value=2)
    )


tab1, tab2 = st.tabs(["Feed", "Short"])

with tab1:
    st.title("Feed")

    news = get_news_from_telegram(channels, banned_topics, news_to_fetch)

    for item in news["filtered_news"]:
        st.markdown(item["text"])
        st.caption(
            f"<span> <p style='float: left'> Source: {item['source']} </p>"
            + f"<p style='float: right'> {item['date']} </p> </span>",
            unsafe_allow_html=True,
        )
        st.divider()

    st.title("Filtered out news")

    for item in news["filtered_out_news"]:
        st.markdown(item["text"])
        st.caption(
            f"<span> <p style='float: left'> Source: {item['source']} </p>"
            + f"<p style='float: right'> {item['date']} </p> </span>",
            unsafe_allow_html=True,
        )
        st.divider()

with tab2:
    st.title("Short")

    news = get_news_from_telegram(
        channels, banned_topics, news_to_fetch, short=True
    )

    for item in news["filtered_news"]:
        st.markdown(item["text"])
        st.caption(
            f"<span> <p style='float: left'> Source: {item['source']} </p>"
            + f"<p style='float: right'> {item['date']} </p> </span>",
            unsafe_allow_html=True,
        )

    st.title("Filtered out news")

    for item in news["filtered_out_news"]:
        st.markdown(item["text"])
        st.caption(
            f"<span> <p style='float: left'> Source: {item['source']} </p>"
            + f"<p style='float: right'> {item['date']} </p> </span>",
            unsafe_allow_html=True,
        )
        st.divider()
