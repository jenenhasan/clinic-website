# create_favicon.py
from PIL import Image, ImageDraw

# Create a 16x16 image
img = Image.new('RGB', (16, 16), color='#0A2E36')
draw = ImageDraw.Draw(img)
draw.text((4, 2), 'M', fill='white')
img.save('static/favicon.ico')
print("✅ Favicon created at static/favicon.ico")

