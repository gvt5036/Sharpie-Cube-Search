import ijson
import os
import json

# Create the directories for each letter and non-alphabetical characters (symbols)
for letter in 'abcdefghijklmnopqrstuvwxyz':
    os.makedirs(f'card_chunks/{letter}', exist_ok=True)
os.makedirs('card_chunks/symbols', exist_ok=True)

# Helper function to write a chunk to a file, ensuring that it's under 50MB
def write_chunk(directory, prefix, chunk, index):
    filename = f'{directory}/{prefix}{index}.json'
    with open(filename, 'w', encoding='utf-8') as out:
        json.dump(chunk, out, indent=2)

# Open the JSON file and stream through it
with open('all-cards.json', 'r', encoding='utf-8') as f:
    objects = ijson.items(f, 'item')  # 'item' refers to the top-level elements in the JSON array
    
    # Variables to track chunking
    chunk = []
    current_size = 0
    current_letter = ''
    current_index = 1  # Start with a1, a2, etc.

    for card in objects:
        first = card.get('name', 'unknown')[0].lower()
        
        # If it's a non-alphabetical character, add it to the 'symbols' directory
        if not first.isalpha():
            first = 'symbols'
        
        # Check the directory to write to (based on first letter or symbol)
        directory = f'card_chunks/{first}'
        
        # Check the size of the card before adding it to the chunk
        card_size = len(json.dumps(card, ensure_ascii=False).encode('utf-8'))
        
        # If the chunk size exceeds 50MB, start a new chunk
        if current_size + card_size > 50 * 1024 * 1024:  # 50MB limit
            write_chunk(directory, first, chunk, current_index)
            current_index += 1  # Increment the chunk index
            chunk = []  # Reset chunk
            current_size = 0  # Reset current size
        
        # Add the card to the current chunk
        chunk.append(card)
        current_size += card_size

    # Write the last chunk if there are any remaining cards
    if chunk:
        write_chunk(directory, first, chunk, current_index)

print("Data split into chunks successfully!")
