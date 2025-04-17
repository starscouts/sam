from nltk.tokenize.treebank import TreebankWordDetokenizer
from os.path import getsize
from tqdm import tqdm
import sqlite3
import nltk
import random

print("Context window: " + str(context_window) + " tokens")
exit()
query = "".join(line for line in disk.iterdump())
db.executescript(query)

c = db.cursor()
detokenizer = TreebankWordDetokenizer()

print("Model loaded.")

input = "Model: Hey! How are you?"
k_value = 1

c.execute("SELECT * FROM Tokens")
context_window = len(c.fetchone()) - 2
print("Found context window of " + str(context_window))


def get_next(context: list[str]) -> str:
    padded_context = context.copy()
    while len(padded_context) < context_window:
        padded_context.insert(0, "")
    context_windowed = padded_context[-context_window:]

    #print(context_windowed)

    for m in range(context_window, 0, -1):
        target = context_windowed.copy()
        #print(target, m)
        target.reverse()
        i = 1

        query = "Before" + str(i) + " = quote(" + target[0].replace("'", "''").replace("?", "\\?") + ")"
        i += 1

        for token in target[1:m]:
            query += " AND Before" + str(i) + " = quote(" + token.replace(")", "\\à") + ")"
            i += 1

        results = {}

        c.execute(f"SELECT * FROM Tokens WHERE " + query)
        print(query)
        #print(f"SELECT * FROM Tokens WHERE " + query)
        #c.execute(f"SELECT * FROM Tokens WHERE " + query + " ORDER BY RANDOM() LIMIT 100")
        data = c.fetchall()

        for entry in data:
            score = 0
            tokens = list(entry[:-2])

            for i in range(len(tokens)):
                if tokens[i] == context_windowed[i]:
                    score += 1

            results[entry[-2]] = score

        guesses_list = []

        for k, v in results.items():
            guesses_list.append({
                'token': k,
                'score': v
            })

        guesses_list = sorted(guesses_list, key=lambda x: x['score'])
        #print(guesses_list)

        if len(guesses_list) > 0:
            nearest = guesses_list[-k_value:]
            return random.choice(nearest)['token']


tokens = nltk.casual_tokenize(input)
completion = [tokens[-1]]
tokens = tokens[:-1]

print(detokenizer.detokenize(list(map(lambda x: "\n\n" if x == "[EOF]" else x, tokens + completion))))

while len(completion) < 64:
    completion.append(get_next(tokens + completion))
    print(detokenizer.detokenize(list(map(lambda x: "\n\n" if x == "[EOF]" else x, tokens + completion))))
