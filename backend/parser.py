import fitz
import os

def smart_parse_pdf(pdf_path):
    doc = fitz.open(os.path.abspath(pdf_path))
    extracted_data = []
    current_section = "Abstract"

    for page_num, page in enumerate(doc):
        # 1. Get dictionary format for font/position data
        blocks = page.get_text("dict")["blocks"]
        
        # 2. Sort for Two-Column Papers
        # We split the page down the middle (mid_x)
        mid_x = page.rect.width / 2
        # Sort: Left column (top-to-bottom) then Right column (top-to-bottom)
        sorted_blocks = sorted(blocks, key=lambda b: (b['bbox'][0] > mid_x + 10, b['bbox'][1]))

        for b in sorted_blocks:
            if "lines" in b:
                block_text = []
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text: continue
                        
                        # Section Detection Logic
                        # Headers are usually larger (11pt+) or Bold
                        is_header = span["size"] > 10.8 or "bold" in span["font"].lower()
                        if is_header and len(text) < 60:
                            current_section = text
                        
                        block_text.append(text)
                
                full_text = " ".join(block_text).strip()
                if len(full_text) > 20:
                    extracted_data.append({
                        "content": full_text,
                        "metadata": {
                            "page": page_num + 1,
                            "section": current_section
                        }
                    })
    
    # CRITICAL: Close the file so Windows can delete it later
    doc.close()
    return extracted_data