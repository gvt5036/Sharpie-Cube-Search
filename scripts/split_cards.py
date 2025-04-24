import json, os
from collections import defaultdict

with open('all-cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

buckets = defaultdict(list)
for card in cards:
    first = card.get('name', 'unknown')[0].lower()
    if not first.isalpha():
        first = 'symbols'
    buckets[first].append(card)

os.makedirs('card_chunks', exist_ok=True)
for key, value in buckets.items():
    with open(f'card_chunks/{key}.json', 'w', encoding='utf-8') as out:
        json.dump(value, out, indent=2)
