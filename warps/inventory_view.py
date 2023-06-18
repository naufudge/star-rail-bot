import os
from PIL import Image, ImageFont, ImageDraw, ImageOps
import random
import math

# thumbs = os.listdir('warps/WarpThumbs')
# random.shuffle(thumbs)

# Actual size of a single thumbnail: (144, 168)
# test = thumbs[0:random.randint(1, 27)] # Test case

# chara_copies = {chara_name : copies}

def inventory_view(inventory_dict: dict):
    thumbs = list(inventory_dict)
    number_of_rows = math.ceil(len(thumbs)/5)
    if number_of_rows <= 1:
        # (3 + 3) * len(thumbs) = taking the border into account
        # (15 + 15) * len(thumbs) = taking the horizontal distance between the thumbnails into account
        width = (144 * len(thumbs)) + (15 * (len(thumbs)+1)) + (6 * len(thumbs))

        # 3 * 2 = taking the border into account
        # 15 * 2 = taking the vertical distance between the thumbnails into account
        height = 168 + (15 * 2) + (3 * 3)
        result = Image.new('RGBA', (width, height), color=0xffffff)
    else:
        width = (144 * 5) + (15 * 6) + (3 * 10)
        height = (168 * number_of_rows) + (15 * (number_of_rows + 1)) + (6 * number_of_rows)
        result = Image.new('RGBA', (width, height), color=0xffffff)

    i = 1
    img_width, img_height = 15, 15

    for chara_name, dupes in inventory_dict.items():
        img = Image.open(f"warps/WarpThumbs/{chara_name}.png")
        img = img.resize((144, 168))

        # Image text writing below
        copies = f"E{dupes}" # COPIES
        title_font = ImageFont.truetype('warps/Misc/NotoSans-Bold.ttf', 22)
        image_editable = ImageDraw.Draw(img)
        image_editable.text((5,0), copies, font=title_font, stroke_width=1, stroke_fill=(0, 0, 0))
        # Image border below
        img = ImageOps.expand(img, border=(3,3,3,3), fill="white")

        result.paste(img, (img_width, img_height))
        img_width = img_width + img.width + 15

        if i == 5:
            img_height += img.height + 15
            img_width = 15
            i = 0
        i += 1

    result_width = int(result.width * 0.65)
    result_height = int(result.height * 0.65)
    result = result.resize((result_width, result_height))

    return result
