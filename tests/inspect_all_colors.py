from PIL import Image
from collections import Counter

def inspect_all_colors():
    img = Image.open('frontend/public/contexora-mark.png')
    img = img.convert('RGBA')
    pixels = list(img.getdata())
    
    # Group colors by rounding to nearest 16 to bin similar shades
    binned = []
    for r, g, b, a in pixels:
        if a > 100: # not transparent
            binned_color = (
                (r // 16) * 16,
                (g // 16) * 16,
                (b // 16) * 16
            )
            binned.append(binned_color)
            
    counter = Counter(binned)
    print("Dominant binned colors (R, G, B) and counts:")
    for color, count in counter.most_common(15):
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        print(f"Hex (approx): {hex_color}, Count: {count}, RGB: {color}")

if __name__ == '__main__':
    inspect_all_colors()
