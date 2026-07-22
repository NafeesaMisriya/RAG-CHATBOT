from PIL import Image
from collections import Counter

def get_dominant_blue():
    img = Image.open('frontend/public/contexora-mark.png')
    img = img.convert('RGBA')
    pixels = list(img.getdata())
    
    # filter for blue pixels: B is significantly larger than R and G, and not transparent
    blue_pixels = []
    for r, g, b, a in pixels:
        if a > 200: # solid pixels
            # check for visible blue accent shades
            if b > 80 and b > r + 30:
                blue_pixels.append((r, g, b))
                
    counter = Counter(blue_pixels)
    most_common = counter.most_common(10)
    print("Most common blue pixels:")
    for color, count in most_common:
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        print(f"Hex: {hex_color}, Count: {count}, RGB: {color}")

if __name__ == '__main__':
    get_dominant_blue()
