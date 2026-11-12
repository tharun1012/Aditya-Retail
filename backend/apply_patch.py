path = "/app/backend/quotation_routes.py"

with open(path, "r") as f:
    content = f.read()

old = '''    elements.append(Paragraph("Product Details", header_style))
    
    # Table header - adjusted column widths for better text display
    table_data = [["#", "Product Details", "MRP", "Offer Price", "Qty", "Total"]]
    
    for idx, item in enumerate(quotation["items"], 1):
        # Format product details with proper line breaks
        brand = item.get('brand', '')
        model = item.get('model_number', '')
        product_name = item.get('product_name', '')
        
        # Truncate description if too long
        description = item.get('description', product_name)
        if len(description) > 80:
            description = description[:77] + "..."
        
        product_details = f"<b>{brand}</b><br/>{model}<br/><font size='7'>{description}</font>"
        
        total = item['offer_price'] * item['quantity']
        
        table_data.append([
            str(idx),
            Paragraph(product_details, normal_style),
            f"₹{item['mrp']:,.0f}",
            f"₹{item['offer_price']:,.0f}",
            str(item['quantity']),
            f"₹{total:,.0f}"
        ])
    
    # Create table with better column widths
    col_widths = [25, 220, 65, 75, 35, 75]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))'''

new = '''    elements.append(Paragraph("Product Details", header_style))
    
    # Table header - adjusted column widths for better text display (added Image column)
    table_data = [["#", "Image", "Product Details", "MRP", "Offer Price", "Qty", "Total"]]

    async def fetch_product_image(url, max_w=36, max_h=36):
        """Fetch a product image and return a ReportLab Image flowable sized
        to fit within max_w x max_h (points), preserving aspect ratio.
        Returns None if the URL is missing or the fetch/decode fails, so the
        caller can fall back to a placeholder without breaking PDF generation."""
        if not url:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status != 200:
                        return None
                    img_bytes = await resp.read()
            img_buffer = io.BytesIO(img_bytes)
            from PIL import Image as PILImage
            pil_img = PILImage.open(img_buffer)
            orig_w, orig_h = pil_img.size
            scale = min(max_w / orig_w, max_h / orig_h)
            img_buffer.seek(0)
            return Image(img_buffer, width=orig_w * scale, height=orig_h * scale)
        except Exception as e:
            logging.warning(f"Quotation PDF: failed to fetch product image {url}: {e}")
            return None

    for idx, item in enumerate(quotation["items"], 1):
        # Format product details with proper line breaks
        brand = item.get('brand', '')
        model = item.get('model_number', '')
        product_name = item.get('product_name', '')
        
        # Truncate description if too long
        description = item.get('description', product_name)
        if len(description) > 80:
            description = description[:77] + "..."
        
        product_details = f"<b>{brand}</b><br/>{model}<br/><font size='7'>{description}</font>"
        
        total = item['offer_price'] * item['quantity']

        image_flowable = await fetch_product_image(item.get('image_url'))
        image_cell = image_flowable if image_flowable else Paragraph("<font size='7' color='grey'>No image</font>", small_style)

        table_data.append([
            str(idx),
            image_cell,
            Paragraph(product_details, normal_style),
            f"₹{item['mrp']:,.0f}",
            f"₹{item['offer_price']:,.0f}",
            str(item['quantity']),
            f"₹{total:,.0f}"
        ])
    
    # Create table with better column widths (added Image column, same total width as before)
    col_widths = [25, 45, 175, 65, 75, 35, 75]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))'''

if old not in content:
    raise SystemExit("OLD BLOCK NOT FOUND — aborting, no changes made.")
if content.count(old) != 1:
    raise SystemExit(f"OLD BLOCK MATCHES {content.count(old)} TIMES — expected exactly 1. Aborting.")

content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Patched successfully.")
