# Image Compressor

<p align="center">
  <img src="image.png" alt="Example"/>
</p>

A simple Python repository to compress images in bulk.

This tool reads image files from an `in` folder, processes them, and saves the compressed versions into an `out` folder. It is designed to be easy to use and easy to adjust depending on the balance you want between image quality, dimensions, and final file size.

## What this project does

This repository helps you reduce the size of common image files automatically.

It can:

- process multiple images at once
- reduce image dimensions
- compress images to make them lighter
- convert images to another format if needed
- try to reach a target file size
- keep things simple through a small set of settings

It is useful if you want to:

- prepare images for the web
- reduce storage space
- send lighter image files
- convert a folder of images quickly

## Main features

- Supports common image formats such as PNG, JPG, JPEG, WEBP, BMP, and TIFF
- Can keep the original format or convert everything to one chosen format
- Lets you reduce image size by scaling dimensions down
- Lets you target an approximate final file size in KB
- Lets you control compression quality for lossy formats
- Can continue reducing dimensions if the file is still too large

## How it works

1. Put your images inside the `in` folder
2. Run the Python script
3. The processed images will be written into the `out` folder

## Requirements

You need:

- Python 3
- Pillow

## Installation

Install the required dependency with:

```bash
pip install pillow
```
## To run 

Bash command (you need to be on the folder)

```bash
python script.py
```

## Folder structure

The project expects this structure:

project/  
├─ script.py  
├─ in/  
└─ out/

- `in/` → place your original images here
- `out/` → the compressed images will be saved here

## Settings you can change

Below are the main settings you can adjust in the script.

### Input and output folders

INPUT_DIR = Path("in")  
OUTPUT_DIR = Path("out")

- `INPUT_DIR`  
    This is the folder where the script looks for the original images.  
    By default, it is the `in` folder.
- `OUTPUT_DIR`  
    This is the folder where the script saves the processed images.  
    By default, it is the `out` folder.

If you want to use different folder names, change these values.

---

### Allowed input formats

INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

This defines which file types the script will process.

- If a file extension is included here, the script will accept it
- If it is not included, the file will be ignored

You can remove formats you do not want to support, or add others if needed.

Examples:

- keep only PNG and JPG:
    
    INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
    
- allow WEBP too:
    
    INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
    

---

### Output format

OUTPUT_FORMAT = "same"

This decides the format of the processed files.

Available options:

- `"same"` → keep the original format when possible
- `"jpeg"` → convert everything to JPG
- `"png"` → convert everything to PNG
- `"webp"` → convert everything to WEBP

How to choose:

- Use `"same"` if you want to preserve the original file type
- Use `"jpeg"` for photos where smaller file size matters
- Use `"png"` if you need lossless output or transparency
- Use `"webp"` if you want strong compression and modern web-friendly files

Example:

OUTPUT_FORMAT = "webp"

This will convert all supported images to WEBP.

---

### Resize factor

SCALE_FACTOR = 0.5

This controls the initial resize of the image dimensions.

- `0.5` means the image width and height are reduced to 50%
- `1.0` means keep the original dimensions
- `0.25` means reduce to 25% of the original dimensions

Important: this applies to both width and height, so reducing dimensions has a strong effect on file size.

Examples:

- keep original size:
    
    SCALE_FACTOR = 1.0
    
- reduce more aggressively:
    
    SCALE_FACTOR = 0.3
    

---

### Target file size

TARGET_SIZE_KB = 100

This is the approximate target size for each output image, in kilobytes.

The script will try to compress the image until it gets close to this value.

Examples:

- target around 100 KB:
    
    TARGET_SIZE_KB = 100
    
- target around 300 KB:
    
    TARGET_SIZE_KB = 300
    
- target around 50 KB:
    
    TARGET_SIZE_KB = 50
    

Note: this is a target, not a guaranteed exact result. Some images cannot go that low without significant quality loss.

---

### Quality range for lossy formats

START_QUALITY = 90  
MIN_QUALITY = 20

These values are used for formats such as JPEG and WEBP.

- `START_QUALITY`  
    The script begins compression from this quality level.
- `MIN_QUALITY`  
    The script will not go below this quality level.

How to think about it:

- higher quality = better image appearance, larger file
- lower quality = smaller file, more visible loss

Examples:

- higher visual quality:
    
    START_QUALITY = 95  
    MIN_QUALITY = 40
    
- stronger compression:
    
    START_QUALITY = 85  
    MIN_QUALITY = 15
    

If you want to preserve more detail, increase `MIN_QUALITY`.  
If you want the smallest files possible, lower it.

---

### Minimum scale factor

MIN_SCALE_FACTOR = 0.2

If the image is still too large after compression, the script can continue reducing its dimensions.

This value sets the minimum resize limit.

- `0.2` means the script can reduce dimensions down to 20% of the original size
- lower values allow more aggressive shrinking
- higher values protect image dimensions more

Examples:

- allow stronger shrinking:
    
    MIN_SCALE_FACTOR = 0.1
    
- prevent too much resizing:
    
    MIN_SCALE_FACTOR = 0.4
    

This is useful when file size is more important than image resolution.

## Recommended default setup

A good balanced starting point is:

OUTPUT_FORMAT = "same"  
SCALE_FACTOR = 0.5  
TARGET_SIZE_KB = 100  
START_QUALITY = 90  
MIN_QUALITY = 20  
MIN_SCALE_FACTOR = 0.2

This setup gives a practical balance between:

- smaller file size
- acceptable visual quality
- simple behavior for most common images

## Tips

- For the smallest files, use `OUTPUT_FORMAT = "webp"`
- For photos, `jpeg` or `webp` usually works best
- For transparent images, `png` or `webp` is often a better choice
- If images still look too large in size, reduce `SCALE_FACTOR`
- If images look too blurry, increase `MIN_QUALITY` or increase `SCALE_FACTOR`
