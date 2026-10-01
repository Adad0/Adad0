from rembg import remove
from PIL import Image, ImageEnhance
import io

# Daha gölgeli ve detaylı bir karakter seti
ASCII_CHARS = ["@", "#", "8", "&", "o", ":", "*", ".", " "]

def scale_image(image, new_width=110):  
    (original_width, original_height) = image.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, new_height))

def map_pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    interval = 256 / len(ASCII_CHARS)
    
    for pixel in pixels:
        if isinstance(pixel, tuple) and len(pixel) > 1 and pixel[1] < 10:
            ascii_str += " " 
        else:
            gray = pixel[0] if isinstance(pixel, tuple) else pixel
            index = int(gray / interval)
            if index >= len(ASCII_CHARS):
                index = len(ASCII_CHARS) - 1
            ascii_str += ASCII_CHARS[index]
    return ascii_str

def create_animated_svg(ascii_str, width, output_file):
    lines = [ascii_str[index: index + width] for index in range(0, len(ascii_str), width)]
    
    svg_start = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="1000" height="800">
    <style>
        text { font-family: monospace; font-size: 9px; fill: #00FF41; }
        .line { opacity: 0; animation: type 0.1s forwards; }
        @keyframes type { to { opacity: 1; } }
    </style>
    <rect width="100%" height="100%" fill="#0D1117" />
'''
    
    svg_css = "    <style>\n"
    svg_texts = ""
    
    delay = 0.5
    y_pos = 20
    
    for i, line in enumerate(lines):
        # HATA BURADAN KAYNAKLANIYORDU: '&' karakterini '&amp;' olarak kodlayarak çözdük.
        safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&#160;')
        
        svg_css += f"        .l{i} {{ animation-delay: {delay:.2f}s; }}\n"
        svg_texts += f'    <text x="20" y="{y_pos}" class="line l{i}">{safe_line}</text>\n'
        delay += 0.03 
        y_pos += 10 

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_start + svg_css + "    </style>\n" + svg_texts + "</svg>")

def main():
    input_path = "profil_foto.jpg"
    output_svg = "animated_profile.svg"

    print("📸 1. Arka plan siliniyor...")
    with open(input_path, 'rb') as i:
        input_bg_removed = remove(i.read())
    
    img = Image.open(io.BytesIO(input_bg_removed)).convert('LA')
    
    print("🎨 2. Detaylar için kontrast artırılıyor...")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0) 
    
    print("🔤 3. ASCII formatına dönüştürülüyor (Yüksek Çözünürlük)...")
    img = scale_image(img)
    ascii_str = map_pixels_to_ascii(img)
    
    print("✨ 4. SVG oluşturuluyor...")
    create_animated_svg(ascii_str, img.width, output_svg)
    
    print("🎉 Bitti! 'animated_profile.svg' dosyasını tarayıcıda tekrar aç.")

if __name__ == "__main__":
    main()