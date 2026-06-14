import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

BOT_USERNAME = "smart_restaurant_bot"
OUTPUT_DIR = "qr_codes"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# PDF setup
pdf_path = os.path.join(OUTPUT_DIR, "Smart_Restaurant_QRs.pdf")
c = canvas.Canvas(pdf_path, pagesize=A4)
width, height = A4

def create_qr_image(table_number):
    url = f"https://t.me/{BOT_USERNAME}?start=table_{table_number}"
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # Create base canvas (white)
    # 300 DPI, let's make it ~1000x1200 pixels
    bg_w, bg_h = 1000, 1300
    base_img = Image.new('RGB', (bg_w, bg_h), 'white')
    draw = ImageDraw.Draw(base_img)
    
    # Try to load a font, otherwise use default
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 90)
        font_medium = ImageFont.truetype("arialbd.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Texts
    title = "Smart Restaurant"
    table_text = f"STOL {table_number}"
    subtitle = "Menyuni ko'rish uchun skaner qiling"
    
    # Calculate positions (center aligned)
    # Draw title
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    draw.text(((bg_w - (title_bbox[2] - title_bbox[0])) / 2, 80), title, fill="black", font=font_large)
    
    # Paste QR Code
    qr_w, qr_h = qr_img.size
    qr_x = (bg_w - qr_w) // 2
    qr_y = 250
    base_img.paste(qr_img, (qr_x, qr_y))
    
    # Draw Table Number
    table_bbox = draw.textbbox((0, 0), table_text, font=font_medium)
    draw.text(((bg_w - (table_bbox[2] - table_bbox[0])) / 2, qr_y + qr_h + 50), table_text, fill="black", font=font_medium)
    
    # Draw Subtitle
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    draw.text(((bg_w - (sub_bbox[2] - sub_bbox[0])) / 2, qr_y + qr_h + 150), subtitle, fill="black", font=font_small)
    
    # Save PNG
    png_path = os.path.join(OUTPUT_DIR, f"table_{table_number}.png")
    base_img.save(png_path, dpi=(300, 300))
    return png_path

# Generate for tables 1 to 10
for i in range(1, 11):
    img_path = create_qr_image(i)
    
    # Add to PDF
    # Draw image centered on A4
    img_w_cm, img_h_cm = 10*cm, 13*cm
    x = (width - img_w_cm) / 2
    y = (height - img_h_cm) / 2
    c.drawImage(img_path, x, y, width=img_w_cm, height=img_h_cm)
    c.showPage()

c.save()
print("QR kodlar muvaffaqiyatli yaratildi: " + OUTPUT_DIR)
