import io
import sys

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

# Monospace karakter genişliği (font-size 9px için ~0.6em) ve satır yüksekliği
CHAR_W = 5.4
LINE_H = 10
FONT_SIZE = 9
PAD_CHARS = 2  # her kenarda bırakılan boşluk (karakter cinsinden)


def crop_grid(lines):
    """Boş satır ve sütunları atar, tüm satırları aynı uzunluğa getirir."""
    width = max(len(l) for l in lines)
    lines = [l.ljust(width) for l in lines]
    rows = [i for i, l in enumerate(lines) if l.strip()]
    cols = [j for l in lines for j, c in enumerate(l) if c != " "]
    top, bottom = rows[0], rows[-1]
    left, right = min(cols), max(cols)
    return [l[left:right + 1] for l in lines[top:bottom + 1]]


def create_animated_svg(lines, output_file):
    lines = crop_grid(lines)
    cols = len(lines[0])
    pad_x = PAD_CHARS * CHAR_W
    pad_y = PAD_CHARS * LINE_H
    text_len = cols * CHAR_W
    svg_w = round(text_len + 2 * pad_x)
    svg_h = round(len(lines) * LINE_H + 2 * pad_y)

    svg_start = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
    <style>
        text {{ font-family: monospace; font-size: {FONT_SIZE}px; fill: #00FF41; }}
        .line {{ opacity: 0; animation: type 0.1s forwards; }}
        @keyframes type {{ to {{ opacity: 1; }} }}
    </style>
    <rect width="100%" height="100%" fill="#0D1117" />
'''

    svg_css = "    <style>\n"
    svg_texts = ""

    delay = 0.5
    y_pos = pad_y + LINE_H - 2

    for i, line in enumerate(lines):
        # '&' karakterini '&amp;' olarak kodlamak şart (aksi halde SVG bozulur).
        safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&#160;')

        svg_css += f"        .l{i} {{ animation-delay: {delay:.2f}s; }}\n"
        # textLength: font ne olursa olsun satır genişliği sabit kalır
        svg_texts += (f'    <text x="{pad_x:g}" y="{y_pos:g}" textLength="{text_len:g}" '
                      f'lengthAdjust="spacing" class="line l{i}">{safe_line}</text>\n')
        delay += 0.03
        y_pos += LINE_H

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_start + svg_css + "    </style>\n" + svg_texts + "</svg>")


def grid_from_svg(path):
    """Mevcut SVG'deki ASCII ızgarasını okur (fotoğrafı yeniden işlemeden yeniden yerleşim için)."""
    import html
    import re
    with open(path, encoding="utf-8") as f:
        texts = re.findall(r'<text[^>]*>(.*?)</text>', f.read())
    return [html.unescape(t).replace(chr(0xA0), ' ') for t in texts]


def main():
    from rembg import remove
    from PIL import Image, ImageEnhance

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
    lines = [ascii_str[i:i + img.width] for i in range(0, len(ascii_str), img.width)]
    
    print("✨ 4. SVG oluşturuluyor...")
    create_animated_svg(lines, output_svg)
    
    print("🎉 Bitti! 'animated_profile.svg' dosyasını tarayıcıda tekrar aç.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--from-svg":
        # python generate_svg.py --from-svg animated_profile.svg
        src = sys.argv[2] if len(sys.argv) > 2 else "animated_profile.svg"
        create_animated_svg(grid_from_svg(src), "animated_profile.svg")
    else:
        main()