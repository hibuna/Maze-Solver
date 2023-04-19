from PIL import Image, ImageDraw, ImageOps


def create_png(path: str, size: tuple[int, int], matrix: list, solution: list):
    png = Image.new(mode="RGB", size=size, color=(0, 0, 0))

    draw = ImageDraw.Draw(png, mode="RGB")
    for cell in matrix:
        draw.point(xy=cell, fill=(255, 255, 255))
    for cell in solution:
        draw.point(xy=cell, fill=(255, 0, 0))

    png = png.rotate(angle=270)  # turn once CCW to equalize row/col to xy
    png = ImageOps.mirror(png)

    png.save(path)
