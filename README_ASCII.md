# ASCII portrait: updating the photo

`generate_svg.py` turns a photo into `animated_profile.svg` (green text on a dark background, typed line by line).
The script removes the background, raises the contrast, converts to ASCII, crops the empty rows and columns, and sizes the SVG `viewBox` to the result.

```
pip install rembg pillow onnxruntime
# put the new photo in this folder as profil_foto.jpg (it is in .gitignore, never commit it)
python generate_svg.py
```

To re-fit the existing SVG without the photo (crop and recompute `viewBox` only):

```
python generate_svg.py --from-svg animated_profile.svg
```

Notes:
- The grid width is set by `scale_image(new_width=110)`. A larger value gives more detail but a taller SVG.
- Each text line has a fixed `textLength`, so the width does not depend on the viewer's monospace font.
- Commit only `animated_profile.svg`, not the photo.
