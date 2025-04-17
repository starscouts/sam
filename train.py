import json
from os.path import exists
from os import unlink
import nltk
from tqdm import tqdm
from os.path import getsize

context_window = 20


if exists("./data/model/sam-1-live.smr"):
    unlink("./data/model/sam-1-live.smr")

db = open("./data/model/sam-1-live.smr", "w")
db.write(chr(0xf0010) + str(context_window) + chr(0xf0020))

with open("./data/training/dataset.txt") as d:
    dataset = d.read().strip().split("\n\n")

for entry in dataset:
    print(entry)

    tokens = nltk.casual_tokenize(entry) + ["[EOF]"]

    last = []

    for token in tokens:
        if len(last) != 0:
            padded_last = last.copy()
            while len(padded_last) < context_window:
                padded_last.insert(0, " ")

            db.write(chr(0xf0030).join(padded_last) + chr(0xf0030) + chr(0xf0040) + token + chr(0xf0050))
        last.append(token)
        last = last[-context_window:]

db.write(chr(0xf0060))
db.close()

print("Formatting model, this may take a while.")
size = getsize("./data/model/sam-1-live.smr")

with tqdm(total=size) as pbar:
    disk = open("./data/model/sam-1-live.smr")
    pos = disk.tell()
    db = {}

    # TODO: Check magic
    disk.read(1)

    context_window_str = ""
    byte = disk.read(1)

    while ord(byte) != 0xf0020:
        context_window_str += byte
        byte = disk.read(1)

    context_window = int(context_window_str)

    while ord(byte) != 0xf0060:
        pbar.update(disk.tell() - pos)
        pos = disk.tell()

        tokens = []
        item = ""
        byte = disk.read(1)

        while ord(byte) != 0xf0040:
            item += byte
            byte = disk.read(1)
            if ord(byte) == 0xf0030:
                tokens.append(item.strip())
                item = ""
                byte = disk.read(1)

        after = ""
        byte = disk.read(1)
        while ord(byte) != 0xf0050:
            after += byte
            byte = disk.read(1)

        tokens = list(filter(lambda x: x != "", tokens))

        for i in range(len(tokens), 0, -1):
            db[chr(0xf0030).join(tokens[:i])] = after

    disk.close()

with open("./data/model/sam-1-live.smf", "w") as f:
    f.write(json.dumps(db))
