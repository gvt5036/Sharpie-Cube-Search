import ijson
import os
from collections import defaultdict
import json

# Create the 'card_chunks' directory if it doesn't exist
os.makedirs('card_chunks', exist_ok=True)

# Initialize the buckets for the cards
buckets = defaultdict(list)

# Open the JSON file and stream through it
with open('all-cards.json', 'r', encoding='utf-8') as f:
    objects = ijson.items(f, 'item')  # 'item' refers to the top-level elements in the JSON array
    for i, card in enumerate(objects):
        if i % 1000 == 0:  # Log every 1000 cards processed
            print(f"Processed {i} cards...")
        first = card.get('name', 'unknown')[0].lower()
        if not first.isalpha():
            first = 'symbols'
        buckets[first].append(card)

# Write out each bucket to a separate file
for key, value in buckets.items():
    with open(f'card_chunks/{key}.json', 'w', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
