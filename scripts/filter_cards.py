import json
import requests
import re

EXCLUDED_LAYOUTS = {
    "token", "double_faced_token", "emblem", "art_series", "vanguard",
    "planar", "scheme", "minigame", "reversible_card", "augment", "host", "token_split"
}

ALLOWED_RARITIES = {"common", "uncommon", "rare", "mythic", "special", "bonus"}

ALLOWED_SETS = {
    "ust", "unh", "ugl", "con", "cn2", "myst"
}

def is_draftable(card):
    if card["lang"] != "en":
        return False
    if card["layout"] in EXCLUDED_LAYOUTS:
        return False
    if not card.get("games") or "paper" not in card["games"]:
        return False
    if card.get("oversized"):
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
    text = text.replace("—", "-")       # Normalize em-dashes
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("’", "'")
    text = re.sub(r'\s+', ' ', text)    # Collapse whitespace
    return text.strip()

def build_printable_text(card):
    # Handle modal or double-faced cards
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
    print("Downloading Scryfall default-cards bulk file...")
    resp = requests.get("https://data.scryfall.io/default-cards/default-cards.json")
    all_cards = resp.json()

    print(f"Total cards: {len(all_cards)}")
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
            "oracle_text": card.get("oracle_text"),
            "flavor_text": card.get("flavor_text"),
            "printable_text": build_printable_text(card)
        }
        filtered.append(filtered_card)

    print(f"Filtered draftable cards: {len(filtered)}")
    with open("filtered_cards.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)

    print("Output saved to filtered_cards.json")

if __name__ == "__main__":
    main()
