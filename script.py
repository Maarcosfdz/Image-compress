from pathlib import Path
from io import BytesIO
from PIL import Image

INPUT_DIR = Path("in")
OUTPUT_DIR = Path("out")

# Allowed input formats
INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

# Output format:
# "same"  -> keep the original format when possible
# "jpeg"  -> convert everything to jpg
# "png"   -> convert everything to png
# "webp"  -> convert everything to webp
OUTPUT_FORMAT = "same"

# Reduce size by half
SCALE_FACTOR = 0.5

# Target approximate size (KB)
TARGET_SIZE_KB = 100

# Initial/final quality for lossy formats
START_QUALITY = 90
MIN_QUALITY = 20

# If still too large, keep reducing dimensions
MIN_SCALE_FACTOR = 0.2


def get_size_kb_from_path(path: Path) -> float:
    return path.stat().st_size / 1024


def get_size_kb_from_bytes(data: bytes) -> float:
    return len(data) / 1024


def normalize_format(ext: str) -> str:
    ext = ext.lower()
    mapping = {
        ".jpg": "jpeg",
        ".jpeg": "jpeg",
        ".png": "png",
        ".webp": "webp",
        ".bmp": "bmp",
        ".tiff": "tiff",
    }
    return mapping.get(ext, "png")


def get_output_format(input_path: Path) -> str:
    if OUTPUT_FORMAT == "same":
        return normalize_format(input_path.suffix)
    return OUTPUT_FORMAT.lower()


def get_output_extension(fmt: str) -> str:
    mapping = {
        "jpeg": ".jpg",
        "png": ".png",
        "webp": ".webp",
        "bmp": ".bmp",
        "tiff": ".tiff",
    }
    return mapping[fmt]


def prepare_image_for_format(img: Image.Image, out_format: str) -> Image.Image:
    """
    Adjust the image according to the output format.
    JPEG doesn't support transparency.
    """
    if out_format == "jpeg":
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            alpha = img.getchannel("A") if "A" in img.getbands() else None
            background.paste(img, mask=alpha)
            return background
        return img.convert("RGB")

    if out_format in ("png", "webp", "tiff"):
        if img.mode not in ("RGB", "RGBA"):
            return img.convert("RGBA")
        return img

    return img.convert("RGB")


def save_to_bytes(img: Image.Image, out_format: str, quality: int | None = None) -> bytes:
    buffer = BytesIO()

    if out_format == "jpeg":
        img.save(
            buffer,
            format="JPEG",
            quality=quality if quality is not None else 85,
            optimize=True,
            progressive=True,
        )

    elif out_format == "webp":
        img.save(
            buffer,
            format="WEBP",
            quality=quality if quality is not None else 80,
            method=6,
        )

    elif out_format == "png":
        # PNG doesn't use quality the same way JPG/WEBP do
        img.save(
            buffer,
            format="PNG",
            optimize=True,
            compress_level=9,
        )

    elif out_format == "bmp":
        img.save(buffer, format="BMP")

    elif out_format == "tiff":
        img.save(buffer, format="TIFF", compression="tiff_deflate")

    else:
        raise ValueError(f"Formato no soportado: {out_format}")

    return buffer.getvalue()


def quantize_png_if_needed(img: Image.Image) -> bytes:
    """
    For PNG, try reducing colors to lower the file size.
    """
    best_data = save_to_bytes(img, "png")
    best_size = get_size_kb_from_bytes(best_data)

    for colors in [256, 128, 64, 32, 16]:
        test_img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors)
        data = save_to_bytes(test_img, "png")
        size = get_size_kb_from_bytes(data)

        if size < best_size:
            best_data = data
            best_size = size

        if size <= TARGET_SIZE_KB:
            return data

    return best_data


def compress_image(img: Image.Image, out_format: str) -> bytes:
    """
    Attempts to get a file below the target size.
    For JPEG/WEBP it lowers quality.
    For PNG it reduces colors.
    If that's not enough, the caller will reduce dimensions.
    """
    img = prepare_image_for_format(img, out_format)

    if out_format == "png":
        return quantize_png_if_needed(img)

    if out_format in ("jpeg", "webp"):
        best_data = None
        best_size = float("inf")

        for quality in range(START_QUALITY, MIN_QUALITY - 1, -5):
            data = save_to_bytes(img, out_format, quality=quality)
            size = get_size_kb_from_bytes(data)

            if size < best_size:
                best_data = data
                best_size = size

            if size <= TARGET_SIZE_KB:
                return data

        return best_data

    return save_to_bytes(img, out_format)


def resize_image(img: Image.Image, scale: float) -> Image.Image:
    new_width = max(1, int(img.width * scale))
    new_height = max(1, int(img.height * scale))
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def process_file(input_path: Path) -> None:
    out_format = get_output_format(input_path)
    output_ext = get_output_extension(out_format)
    output_path = OUTPUT_DIR / f"{input_path.stem}{output_ext}"

    with Image.open(input_path) as img:
        img.load()

        current_scale = SCALE_FACTOR
        resized = resize_image(img, current_scale)
        best_data = compress_image(resized, out_format)
        best_size = get_size_kb_from_bytes(best_data)

        while best_size > TARGET_SIZE_KB and current_scale > MIN_SCALE_FACTOR:
            current_scale *= 0.85
            resized = resize_image(img, current_scale)
            data = compress_image(resized, out_format)
            size = get_size_kb_from_bytes(data)

            if size < best_size:
                best_data = data
                best_size = size

            if size <= TARGET_SIZE_KB:
                best_data = data
                best_size = size
                break

        output_path.write_bytes(best_data)

        print(
            f"{input_path.name} -> {output_path.name} | "
            f"{get_size_kb_from_path(input_path):.1f} KB -> {best_size:.1f} KB"
        )


def main() -> None:
    if not INPUT_DIR.exists():
        print(f"No existe la carpeta de entrada: {INPUT_DIR.resolve()}")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    files = [
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in INPUT_EXTENSIONS
    ]

    if not files:
        print("No se encontraron imágenes compatibles en la carpeta 'in'.")
        return

    for file_path in sorted(files):
        try:
            process_file(file_path)
        except Exception as e:
            print(f"Error con {file_path.name}: {e}")

    print("Terminado.")


if __name__ == "__main__":
    main()