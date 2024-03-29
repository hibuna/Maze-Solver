from PIL import Image, ImageDraw, ImageOps


def create_png(path: str, size: tuple[int, int], matrix: list, solution: list):
    png = Image.new(mode="RGB", size=size, color=(0, 0, 0))
    draw = ImageDraw.Draw(png, mode="RGB")
    for cell in matrix:
        draw.point(xy=cell, fill=(255, 255, 255))

    red_base, green_base = 255, 0
    gradient_increment = 255 / len(solution)
    for i, cell in enumerate(solution):
        red = red_base - round(i * gradient_increment)
        green = green_base + round(i * gradient_increment)
        red = 0 if red < 0 else red
        green = 255 if green > 255 else green
        draw.point(xy=cell, fill=(red, green, 0))

    png = png.rotate(angle=270)  # row/col != xy
    png = ImageOps.mirror(png)

    png.save(path)
