import ijson
import os
from collections import defaultdict
import json

# Create the output directory if it doesn't exist
os.makedirs('card_chunks', exist_ok=True)

# Prepare buckets by first character of card name
buckets = defaultdict(list)

# Stream parse the large JSON file
with open('all-cards.json', 'r', encoding='utf-8') as f:
    cards = ijson.items(f, 'item')  # For top-level array

    for i, card in enumerate(cards):
        if i % 1000 == 0:
            print(f"Processed {i} cards...")

        first = card.get('name', 'unknown')[0].lower()
        if not first.isalpha():
            first = 'symbols'
        buckets[first].append(card)

# Write each bucket to its own file
for key, value in buckets.items():
    with open(f'card_chunks/{key}.json', 'w', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
