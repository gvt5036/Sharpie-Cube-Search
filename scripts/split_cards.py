import ijson
import os
import json
from collections import defaultdict
from decimal import Decimal

# Create the 'card_chunks' directory if it doesn't exist
os.makedirs('card_chunks', exist_ok=True)

# Initialize the buckets for the cards
buckets = defaultdict(list)

# Function to handle Decimal serialization
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Type not serializable")

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

# Write out each bucket to a separate file, ensuring size limits are respected
for key, value in buckets.items():
    chunk_index = 1
    current_chunk = []
    current_size = 0

    for card in value:
        # Get the size of the card's JSON representation
        card_size = len(json.dumps(card, ensure_ascii=False, default=decimal_default).encode('utf-8'))
        
        # If adding this card would exceed the size limit, start a new chunk
        if current_size + card_size > 50 * 1024 * 1024:  # 50 MB
            with open(f'card_chunks/{key}/{key}{chunk_index}.json', 'w', encoding='utf-8') as out:
                json.dump(current_chunk, out, ensure_ascii=False, indent=2, default=decimal_default)
            chunk_index += 1
            current_chunk = [card]
            current_size = card_size
        else:
            current_chunk.append(card)
            current_size += card_size

    # Write the last chunk if it contains any cards
    if current_chunk:
        with open(f'card_chunks/{key}/{key}{chunk_index}.json', 'w', encoding='utf-8') as out:
            json.dump(current_chunk, out, ensure_ascii=False, indent=2, default=decimal_default)
