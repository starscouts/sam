from os import listdir
from os.path import isdir
import json

signal = listdir("./data/training/signal")
t = open("./data/training/dataset.txt", "w")

for folder in signal:
    if not isdir(f"./data/training/signal/{folder}"):
        continue
    with open(f"./data/training/signal/{folder}/data.json") as f:
        data = map(lambda x: json.loads(x), f.readlines())
        for message in data:
            if message['body'].strip() != "":
                source = "Model:" if message['sender'] == "Me" else "User:"
                message['body'] = message['body'].replace("￼", "")

                message = f"{source} {message['body'].strip()}"
                print(message)
                t.write(f"{message}\n\n")

t.close()
