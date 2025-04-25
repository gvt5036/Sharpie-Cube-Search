import json
import requests
import re
import os

# Layouts that are not draftable/playable
EXCLUDED_LAYOUTS = {
    "token", "double_faced_token", "emblem", "art_series", "vanguard",
    "planar", "scheme", "minigame", "reversible_card", "augment", "host", "token_split"
}

# Rarities typically associated with draftable cards
ALLOWED_RARITIES = {"common", "uncommon", "rare", "mythic", "special", "bonus"}

# Include these sets even if rarity is nonstandard
ALLOWED_SETS = {"ust", "unh", "ugl", "con", "cn2", "myst"}

# Directory to store output
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "filtered_cards.json")

def is_draftable(card):
    if card["lang"] != "en":
        return False
    if card["layout"] in EXCLUDED_LAYOUTS:
        return False
    if not card.get("games") or "paper" not in card["games"]:
        return False
    if card.get("oversized"):
        return False

    # Exclude basic lands with no flavor text
    if "Basic Land" in card.get("type_line", "") and not card.get("flavor_text"):
        return False

    rarity = card.get("rarity")
    if rarity in ALLOWED_RARITIES:
        return True
    if card.get("set") in ALLOWED_SETS:
        return True

    return False

def normalize_text(text):
    if not text:
        return ""
    text = text.replace("—", "-")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("’", "'")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def build_printable_text(card):
    faces = card.get("card_faces")
    parts = []
    if faces:
        for face in faces:
            text = normalize_text(face.get("oracle_text", ""))
            flavor = normalize_text(face.get("flavor_text", ""))
            if text:
                parts.append(text)
            if flavor:
                parts.append(flavor)
    else:
        text = normalize_text(card.get("oracle_text", ""))
        flavor = normalize_text(card.get("flavor_text", ""))
        if text:
            parts.append(text)
        if flavor:
            parts.append(flavor)

    return " ".join(parts)

def main():
    print("Fetching Scryfall bulk metadata...")
    meta_resp = requests.get("https://api.scryfall.com/bulk-data")
    meta_resp.raise_for_status()
    meta = meta_resp.json()

    bulk = next(b for b in meta["data"] if b["type"] == "default_cards")

    print("Downloading default-cards JSON...")
    download_resp = requests.get(bulk["download_uri"])
    download_resp.raise_for_status()
    all_cards = download_resp.json()

    print(f"Total cards fetched: {len(all_cards)}")
    filtered = []

    for card in all_cards:
        if not is_draftable(card):
            continue
        filtered_card = {
            "id": card["id"],
            "name": card["name"],
            "set": card["set"],
            "collector_number": card["collector_number"],
            "layout": card.get("layout"),
            "type_line": card.get("type_line"),
            "colors": card.get("colors"),
            "cmc": card.get("cmc"),
            "power": card.get("power"),
            "toughness": card.get("toughness"),
            "oracle_text": card.get("oracle_text"),
            "flavor_text": card.get("flavor_text"),
            "printable_text": build_printable_text(card)
        }
        filtered.append(filtered_card)

    print(f"Draftable cards retained: {len(filtered)}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print(f"Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
