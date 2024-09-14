import ollama


def text_contains_topic(banned_topics, text):
    prompt = f"""{text} 
    Does this text contain information about any of these topics: {', '.join(banned_topics).lower()}? Only output [yes] or [no]"""
    print(prompt)
    output = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        options={"num_predict": 10, "seed": 42, "temperature": 0.6},
    )

    print(output["message"]["content"])
    print("-------------------")

    return "[yes]" in output["message"]["content"]


def shorten_text(text):
    prompt = f"""{text}

    Shorten this text to only one sentence."""
    print(prompt)
    output = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        options={"num_predict": 100, "seed": 42},
    )

    print(output["message"]["content"])
    print("-------------------")

    return output["message"]["content"]
