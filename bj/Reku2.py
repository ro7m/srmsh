import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io

def add_large_diagonal_watermark(image, watermark_text):
    # Create a transparent overlay for the watermark
    watermark = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Calculate watermark size (40% of page height)
    watermark_height = int(image.height * 0.4)
    
    # Find appropriate font size
    try:
        # Start with a reasonable font size and adjust
        font_size = int(watermark_height / (len(watermark_text.split('\n')) * 2))
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            # For default font, we'll use a fixed approach
    
    # Split text into lines
    lines = watermark_text.split('\n')
    
    # Adjust font size to fit the desired height
    if 'truetype' in str(type(font)):
        # For TrueType fonts, we can adjust size
        while True:
            line_heights = []
            line_widths = []
            for line in lines:
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_widths.append(bbox[2] - bbox[0])
                    line_heights.append(bbox[3] - bbox[1])
                except:
                    break
            
            if not line_heights:
                break
                
            total_height = sum(line_heights) + (len(lines) - 1) * 10
            max_width = max(line_widths) if line_widths else 0
            
            # Check if we need to adjust font size
            if total_height < watermark_height * 0.8 and max_width < image.width * 0.8:
                font_size = int(font_size * 1.1)  # Increase by 10%
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        break
            elif total_height > watermark_height * 1.2:
                font_size = int(font_size * 0.9)  # Decrease by 10%
                try:
                    font = ImageFont.truetype("arialbd.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        break
            else:
                break  # Font size is good
    
    # Create text block with final font
    line_heights = []
    line_widths = []
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
        except:
            line_widths.append(100)
            line_heights.append(30)
    
    total_height = sum(line_heights) + (len(lines) - 1) * 10
    max_width = max(line_widths) if line_widths else 200
    
    # Create a separate image for the watermark text block
    text_block = Image.new('RGBA', (max_width, int(total_height)), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_block)
    
    # Draw each line of text
    y_offset = 0
    for i, line in enumerate(lines):
        try:
            bbox = text_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
        except:
            line_width = 100
            
        x_offset = (max_width - line_width) // 2  # Center each line
        text_draw.text((x_offset, y_offset), line, font=font, fill=(255, 0, 0, 128))
        
        if i < len(line_heights):
            y_offset += line_heights[i] + 10  # Add spacing
        else:
            y_offset += 30 + 10
    
    # Rotate the text block (45 degrees for diagonal)
    rotated_text = text_block.rotate(45, expand=True)
    
    # Position the watermark in the center of the page
    x = (image.width - rotated_text.width) // 2
    y = (image.height - rotated_text.height) // 2
    
    # Paste the watermark onto the page
    watermark.paste(rotated_text, (x, y), rotated_text)
    
    # Combine original image with watermark
    watermarked = Image.alpha_composite(image.convert('RGBA'), watermark)
    return watermarked.convert('RGB')

def convert_pdf_to_watermarked_images(pdf_path, output_prefix="page", dpi=200):
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    # Define multiline watermark text
    watermark_text = "COPY FOR\nREFERENCE\nONLY"
    
    # Process each page
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document[page_num]
        
        # Render page to image
        mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default DPI
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        image = Image.open(io.BytesIO(img_data))
        
        # Add large diagonal watermark
        watermarked_page = add_large_diagonal_watermark(image, watermark_text)
        
        # Save image
        output_filename = f"{output_prefix}_{page_num + 1}.png"
        watermarked_page.save(output_filename, "PNG")
        print(f"Saved: {output_filename}")
    
    # Close the PDF
    pdf_document.close()

# Example usage
if __name__ == "__main__":
    convert_pdf_to_watermarked_images("input.pdf")
