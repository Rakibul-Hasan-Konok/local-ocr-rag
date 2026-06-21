import requests


def generate_answer(query: str, contexts: list):
    context_text = "\n\n".join(contexts)

    prompt = f"""
You are a helpful local document analysis assistant.

Instructions:
1. Read the provided context carefully.
2. Answer in the same language as the question.
3. Give a detailed but clear answer.
4. Include important details from the document.
5. Do not invent information.
6. If the answer is not found, say:
"The answer was not found in the uploaded documents."

Context:
{context_text}

Question:
{query}

Detailed Answer:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]