import json

with open(r"C:\Projects\FSM-NIDS\scripts\editorial_slides_dump.json", "r", encoding="utf-8") as f:
    slides = json.load(f)

for s in slides[6:]:
    print(f"\n================ SLIDE {s['slide']} ================")
    for block in s['text_blocks']:
        print("--- BLOCK ---")
        print(block[:180])
