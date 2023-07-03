from PIL import Image, ImageFont, ImageDraw, ImageOps
import math
import json


def human_format(num: int):
    """
    Changes long numbers to short form. Eg: 10,000 -> 10K
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def charas_by_rarity_sort(initial_dict: dict):
    with open('warps/data/all_warps.json', 'r') as all_warps_data_file:
        chara_and_wpn_data = json.load(all_warps_data_file)

    list_of_owned_charas = list(initial_dict)
    list_of_owned_charas_with_rarity = sorted([(chara_and_wpn_data[chara]['rarity'], chara) for chara in list_of_owned_charas], reverse=True)

    new_dict_of_owned_charas, chara_rarity = {}, {}

    for (rarity, chara) in list_of_owned_charas_with_rarity:
        new_dict_of_owned_charas[chara] = initial_dict[chara]
        chara_rarity[chara] = rarity

    return (new_dict_of_owned_charas, chara_rarity)


def inventory_view(inventory_dict: dict):
    if inventory_dict == {}:
        return None

    owned_chara_and_rarity = charas_by_rarity_sort(inventory_dict)
    ordered_inv_dict = owned_chara_and_rarity[0]
    chara_rarity = owned_chara_and_rarity[1]

    thumbs = list(ordered_inv_dict)
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

    for chara_name, dupes in ordered_inv_dict.items():
        img = Image.open(f"warps/WarpThumbs/{chara_name}.png")
        img = img.resize((144, 168))

        # Image text writing below
        copies = f"E{human_format(dupes)}" # COPIES
        title_font = ImageFont.truetype('warps/Misc/NotoSans-Bold.ttf', 24)
        image_editable = ImageDraw.Draw(img)
        image_editable.text((5,0), copies, font=title_font, stroke_width=2, stroke_fill=(0, 0, 0))
        # Image border below
        if chara_rarity[chara_name] == 4:
            img = ImageOps.expand(img, border=(3,3,3,3), fill="#a000c8")
        elif chara_rarity[chara_name] == 5:
            img = ImageOps.expand(img, border=(3,3,3,3), fill="#edcb01")

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
