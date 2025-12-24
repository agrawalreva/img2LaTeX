#!/usr/bin/env python3
"""
Create sample mathematical images for the img2LaTeX AI application.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

def create_sample_images():
    """Create sample mathematical images."""
    
    # Create output directory
    output_dir = "apps/api/static/samples"
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample mathematical expressions
    samples = [
        {
            "id": "gaussian_integral",
            "name": "Gaussian Integral",
            "description": "The famous Gaussian integral",
            "expected_latex": "\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}",
            "text": "∫₋∞^∞ e^(-x²) dx = √π"
        },
        {
            "id": "quadratic_formula", 
            "name": "Quadratic Formula",
            "description": "The quadratic formula for solving ax² + bx + c = 0",
            "expected_latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
            "text": "x = (-b ± √(b² - 4ac)) / 2a"
        },
        {
            "id": "eulers_identity",
            "name": "Euler's Identity", 
            "description": "Euler's famous identity relating e, i, π, and 1",
            "expected_latex": "e^{i\\pi} + 1 = 0",
            "text": "e^(iπ) + 1 = 0"
        },
        {
            "id": "pythagorean_theorem",
            "name": "Pythagorean Theorem",
            "description": "The fundamental theorem of right triangles",
            "expected_latex": "a^2 + b^2 = c^2",
            "text": "a² + b² = c²"
        }
    ]
    
    for sample in samples:
        # Create image
        width, height = 400, 200
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            # Try to load a system font
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            except:
                font = ImageFont.load_default()
        
        # Draw the mathematical expression
        text = sample["text"]
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with a subtle shadow
        draw.text((x + 2, y + 2), text, fill='lightgray', font=font)
        draw.text((x, y), text, fill='black', font=font)
        
        # Add a subtle border
        draw.rectangle([0, 0, width-1, height-1], outline='lightgray', width=2)
        
        # Save the image
        filename = f"{sample['id']}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath, 'PNG')
        print(f"Created: {filepath}")
    
    print(f"\nCreated {len(samples)} sample images in {output_dir}")

if __name__ == "__main__":
    create_sample_images()
