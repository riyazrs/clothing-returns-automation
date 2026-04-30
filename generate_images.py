"""
Generate 10 synthetic garment images for the clothing returns demo.
Each image has visual cues matching the expected defect scenario.
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), "data", "images")
os.makedirs(OUT, exist_ok=True)

W, H = 400, 500

def base_garment(draw, label, color):
    draw.rectangle([50, 80, 350, 450], fill=color, outline="black", width=2)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    draw.text((W // 2, 30), label, fill="black", anchor="mm", font=font)

def save(img, name):
    img.save(os.path.join(OUT, name), "JPEG", quality=90)
    print(f"  Created: {name}")

# 1. jacket_damaged.jpg - tear/damage
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "JACKET", "#4A6741")
# Draw a visible tear/rip
d.line([(180, 200), (220, 260), (200, 320)], fill="black", width=4)
d.line([(185, 210), (230, 250)], fill="#3A5731", width=6)
d.text((200, 380), "VISIBLE TEAR", fill="red", anchor="mm")
save(img, "jacket_damaged.jpg")

# 2. jeans_clean.jpg - no defect
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "JEANS", "#3B5998")
d.text((200, 265), "CLEAN - NO DEFECTS", fill="white", anchor="mm")
save(img, "jeans_clean.jpg")

# 3. tshirt_stain.jpg - stain
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "T-SHIRT", "#FFFFFF")
# Draw stain blotches
d.ellipse([150, 180, 250, 260], fill="#8B4513")
d.ellipse([160, 200, 230, 250], fill="#A0522D")
d.ellipse([170, 170, 220, 220], fill="#6B3410")
d.text((200, 380), "COFFEE STAIN", fill="red", anchor="mm")
save(img, "tshirt_stain.jpg")

# 4. underwear.jpg - hygiene item (won't reach AI, but needs an image)
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "UNDERWEAR", "#FFB6C1")
d.text((200, 265), "HYGIENE ITEM", fill="black", anchor="mm")
save(img, "underwear.jpg")

# 5. dress_tear.jpg - tear
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "DRESS", "#C71585")
# Draw tear
d.line([(160, 250), (200, 300), (180, 350)], fill="black", width=4)
d.line([(165, 260), (210, 290)], fill="#A71565", width=5)
d.text((200, 400), "FABRIC TEAR", fill="red", anchor="mm")
save(img, "dress_tear.jpg")

# 6. hoodie_clean.jpg - no defect (but final sale, won't reach AI)
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "HOODIE", "#808080")
d.text((200, 265), "CLEAN - NO DEFECTS", fill="white", anchor="mm")
save(img, "hoodie_clean.jpg")

# 7. coat_pilling.jpg - pilling
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "WINTER COAT", "#2F4F4F")
# Draw pilling dots
import random
random.seed(42)
for _ in range(80):
    x = random.randint(80, 320)
    y = random.randint(120, 420)
    r = random.randint(2, 5)
    d.ellipse([x-r, y-r, x+r, y+r], fill="#4F6F6F")
d.text((200, 460), "SURFACE PILLING", fill="red", anchor="mm")
save(img, "coat_pilling.jpg")

# 8. trousers_clean.jpg - no defect
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "TROUSERS", "#2E8B57")
d.text((200, 265), "CLEAN - NO DEFECTS", fill="white", anchor="mm")
save(img, "trousers_clean.jpg")

# 9. swimwear.jpg - hygiene item (won't reach AI)
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "SWIMWEAR", "#00CED1")
d.text((200, 265), "HYGIENE ITEM", fill="black", anchor="mm")
save(img, "swimwear.jpg")

# 10. blazer_missing_button.jpg - missing button
img = Image.new("RGB", (W, H), "#F0F0F0")
d = ImageDraw.Draw(img)
base_garment(d, "BLAZER", "#191970")
# Draw button column - one missing
for i, y in enumerate([180, 240, 300, 360]):
    if i == 1:  # missing button
        d.ellipse([190, y-8, 210, y+8], outline="red", width=2)
        d.line([(192, y-6), (208, y+6)], fill="red", width=2)
        d.line([(208, y-6), (192, y+6)], fill="red", width=2)
    else:
        d.ellipse([190, y-8, 210, y+8], fill="#C0C0C0", outline="black")
d.text((200, 430), "MISSING BUTTON", fill="red", anchor="mm")
save(img, "blazer_missing_button.jpg")

print("\nAll 10 images generated successfully.")
