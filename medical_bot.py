import requests
import os
import sys

API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
headers = {"Authorization": "Bearer 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"}
text_path = 'json/text'
context = ""
question = ""
count = 0

def ask_question(context, question):
    payload = {"inputs": {"question": question, "context": context}}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

with open(os.path.join(text_path, "2019 05-19 Santa Clara Valleypage000.txt"), 'r', encoding='utf-8-sig') as ff:
    context = ff.read()

if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 1:
        question = 'who is author?'
    else:
        for arg in args:
            count = count + 1
            if count > 1:
                question = question + args[count-1] + ' '

    answer = ask_question(context, question)
    print(answer["answer"])
