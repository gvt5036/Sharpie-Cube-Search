import json
import os
from decimal import Decimal
import ijson

# Ensure output directory exists
os.makedirs('card_chunks', exist_ok=True)

# Custom serializer for Decimal objects
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

# Group cards by starting character
grouped_cards = {}

with open('all-cards.json', 'rb') as f:
    cards = ijson.items(f, 'item')
    for card in cards:
        name = card.get('name', '')
        key = name[0].lower() if name and name[0].isalpha() else 'symbols'
        grouped_cards.setdefault(key, []).append(card)

# Write each group to multiple chunk files if needed
for key, cards in grouped_cards.items():
    chunk_index = 1
    current_chunk = []
    current_size = 0

    for card in cards:
        # Estimate size in bytes
        card_size = len(json.dumps(card, ensure_ascii=False, default=decimal_default).encode('utf-8'))

        # If chunk would exceed 50MB, write current chunk to file
        if current_size + card_size > 50 * 1024 * 1024:
            os.makedirs(f'card_chunks/{key}', exist_ok=True)
            with open(f'card_chunks/{key}/{key}{chunk_index}.json', 'w', encoding='utf-8') as out:
                json.dump(current_chunk, out, ensure_ascii=False, indent=2, default=decimal_default)
            chunk_index += 1
            current_chunk = [card]
            current_size = card_size
        else:
            current_chunk.append(card)
            current_size += card_size

    # Write remaining cards
    if current_chunk:
        os.makedirs(f'card_chunks/{key}', exist_ok=True)
        with open(f'card_chunks/{key}/{key}{chunk_index}.json', 'w', encoding='utf-8') as out:
            json.dump(current_chunk, out, ensure_ascii=False, indent=2, default=decimal_default)
