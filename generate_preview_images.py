#!/usr/bin/env python3
"""
Generate BroBro preview images for GHL marketplace
Creates 3 professional 960x540 PNG images
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_preview_image(filename, bg_color, title, subtitle):
    """Create a 960x540 preview image"""
    # Create image
    img = Image.new('RGB', (960, 540), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default
    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_subtitle = ImageFont.truetype("arial.ttf", 40)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()

    # Draw text
    # Title
    bbox_title = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox_title[2] - bbox_title[0]
    title_x = (960 - title_width) // 2
    draw.text((title_x, 180), title, fill='white', font=font_title)

    # Subtitle
    bbox_subtitle = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = bbox_subtitle[2] - bbox_subtitle[0]
    subtitle_x = (960 - subtitle_width) // 2
    draw.text((subtitle_x, 300), subtitle, fill='white', font=font_subtitle)

    # Save
    img.save(filename)
    print(f"[OK] Created: {filename}")

# Create output directory if it doesn't exist
output_dir = r"C:\Users\justi\BroBro"

# Create the 3 preview images
print("Generating BroBro Preview Images...\n")

create_preview_image(
    os.path.join(output_dir, "BroBro_Preview_Image_1.png"),
    (74, 144, 226),  # Blue
    "BroBro",
    "AI Assistant"
)

create_preview_image(
    os.path.join(output_dir, "BroBro_Preview_Image_2.png"),
    (80, 200, 120),  # Green
    "Get Instant",
    "Answers 24/7"
)

create_preview_image(
    os.path.join(output_dir, "BroBro_Preview_Image_3.png"),
    (255, 107, 107),  # Red
    "Powered By",
    "Advanced AI"
)

print("\n[SUCCESS] All 3 preview images created successfully!")
print(f"\nImages saved to: {output_dir}")
print("\nReady to upload to GHL marketplace:")
print("  1. BroBro_Preview_Image_1.png")
print("  2. BroBro_Preview_Image_2.png")
print("  3. BroBro_Preview_Image_3.png")
