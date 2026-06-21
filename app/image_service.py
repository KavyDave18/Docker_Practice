from PIL import Image


def process_image(
    input_path: str,
    output_path: str
):
    """
    Resize and compress image.
    """

    image = Image.open(input_path)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image.thumbnail(
        (800, 800)
    )

    image.save(
        output_path,
        format="JPEG",
        optimize=True,
        quality=60
    )