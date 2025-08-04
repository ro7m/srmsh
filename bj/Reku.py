import PyPDF2
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

def add_diagonal_watermark(image, watermark_text):
    # Create a transparent overlay for the watermark
    watermark = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Try to use a bold font for better visibility, fallback to default
    try:
        font = ImageFont.truetype("arialbd.ttf", 36)  # Bold Arial
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
    
    # Split text into lines
    lines = watermark_text.split('\n')
    
    # Calculate total text block height
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    
    total_height = sum(line_heights) + (len(lines) - 1) * 10  # 10px spacing
    max_width = max(line_widths)
    
    # Create a separate image for the watermark text block
    text_block = Image.new('RGBA', (max_width, int(total_height)), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_block)
    
    # Draw each line of text
    y_offset = 0
    for i, line in enumerate(lines):
        bbox = text_draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x_offset = (max_width - line_width) // 2  # Center each line
        text_draw.text((x_offset, y_offset), line, font=font, fill=(255, 0, 0, 128))
        y_offset += line_heights[i] + 10  # Add spacing
    
    # Rotate the text block (45 degrees for diagonal)
    rotated_text = text_block.rotate(45, expand=True)
    
    # Tile the rotated text across the image
    gap_x = rotated_text.width + 100  # Horizontal spacing between watermarks
    gap_y = rotated_text.height + 100  # Vertical spacing between watermarks
    
    for y in range(-gap_y, image.height + gap_y, gap_y):
        for x in range(-gap_x, image.width + gap_x, gap_x):
            watermark.paste(rotated_text, (x, y), rotated_text)
    
    # Combine original image with watermark
    watermarked = Image.alpha_composite(image.convert('RGBA'), watermark)
    return watermarked.convert('RGB')

def convert_pdf_to_watermarked_images(pdf_path, output_prefix="page"):
    # Convert PDF to list of images
    pages = convert_from_path(pdf_path)
    
    # Define multiline watermark text
    watermark_text = "COPY FOR\nREFERENCE\nONLY"
    
    # Process each page
    for i, page in enumerate(pages):
        # Add diagonal watermark
        watermarked_page = add_diagonal_watermark(page, watermark_text)
        
        # Save image
        output_filename = f"{output_prefix}_{i+1}.png"
        watermarked_page.save(output_filename, "PNG")
        print(f"Saved: {output_filename}")

# Example usage
if __name__ == "__main__":
    convert_pdf_to_watermarked_images("input.pdf")
