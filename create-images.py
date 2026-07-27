# create_images.py
# Run this to create placeholder images: python create_images.py

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_images():
    os.makedirs('static/img', exist_ok=True)
    
    colors = {
        'hero-main': (10, 46, 54),
        'footer-bg': (6, 27, 32),
        'hero-page': (18, 63, 73),
        'cta-banner': (6, 27, 32)
    }
    
    texts = {
        'hero-main': ('Marsh Family Practice', 'Your Health, Our Priority'),
        'footer-bg': ('Marsh Family Practice', 'Comprehensive Care'),
        'hero-page': ('Marsh Family Practice', 'About Us'),
        'cta-banner': ('Marsh Family Practice', 'Book Your Appointment Today')
    }
    
    sizes = {
        'hero-main': (1920, 1080),
        'footer-bg': (1920, 400),
        'hero-page': (1920, 600),
        'cta-banner': (1920, 400)
    }
    
    for name, size in sizes.items():
        img = Image.new('RGB', size, colors[name])
        draw = ImageDraw.Draw(img)
        
        # Draw a border
        draw.rectangle([20, 20, size[0]-20, size[1]-20], outline=(200, 150, 62), width=2)
        
        # Draw text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text1, text2 = texts[name]
        draw.text((size[0]//2, size[1]//2 - 30), text1, fill=(200, 150, 62), anchor="mm", font=font)
        draw.text((size[0]//2, size[1]//2 + 40), text2, fill=(255, 255, 255, 128), anchor="mm", font=font)
        
        img.save(f'static/img/{name}.jpg')
        print(f"✅ Created static/img/{name}.jpg")
    
    print("\n✅ All placeholder images created successfully!")

if __name__ == "__main__":
    create_placeholder_images()