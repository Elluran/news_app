import ollama
from groq import Groq
import redis
import httpx
from httpx_socks import SyncProxyTransport
import tomli
import functools
import os


with open("creds.toml", "rb") as f:
    creds = tomli.load(f)

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=0,
    password=creds["redis"]["password"],
)

if "proxy" in creds["llm"]:
    transport = SyncProxyTransport.from_url(creds["llm"]["proxy"])
    httpx_client = httpx.Client(transport=transport)
)
transport = SyncProxyTransport.from_url(creds["llm"]["proxy"])
httpx_client = httpx.Client(transport=transport)


def ask_model(host, prompt, max_tokens, seed, temperature=None):
    if host == "local":
        output = ollama.chat(
            model="llama3.1:8b",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            options={
                "num_predict": max_tokens,
                "seed": seed,
                "temperature": max_tokens,
            },
        )
        return output["message"]["content"]
    elif host == "groq":
        client = Groq(
            api_key=creds["llm"]["groq_api_key"],
            http_client=httpx_client if "proxy" in creds["llm"] else None,
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-70b-8192",
            # model="gemma2-9b-it",
            max_tokens=max_tokens,
            seed=seed,
            temperature=temperature,
        )

        output = chat_completion.choices[0].message.content
        return output


def text_contains_topic(banned_topics, text):
    prompt = f"""{text} 
    Does this text contain information about any of these topics: {', '.join(banned_topics).lower()}? Only output [yes] or [no]"""

    print(prompt, flush=True)

    if text := redis_client.get(prompt):
        output = text.decode("utf-8")
        print("found output in cache")
    else:
        output = ask_model(
            "groq", prompt, max_tokens=10, seed=42, temperature=0.6
        )
        redis_client.set(prompt, output)

    print(output, flush=True)
    print("-------------------")

    return "[yes]" in output


def shorten_text(text):
    # prompt = f"""{text}

    # Shorten this text to only one sentence."""
    prompt = f"""{text}

Сократи данный текст до одного предложения на русском языке: """
    print(prompt, flush=True)

    if text := redis_client.get(prompt):
        output = text.decode("utf-8")
        print("found output in cache")
    else:
        output = ask_model(
            "groq", prompt, max_tokens=100, seed=42, temperature=0.6
        )
        redis_client.set(prompt, output)

    print(output, flush=True)
    print("-------------------")

    return output
