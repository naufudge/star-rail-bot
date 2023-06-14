from PIL import Image
import os
import random
import threading

def randomizer(dir = None):
    images = os.listdir(dir)
    selected = []
    i = 0
    while i < 10:
        selection = random.choice(images)
        if selection not in selected and selection != "warp_cards.py":
            selected.append(selection)
            i += 1
    return selected

def rotator(paste_img, background: Image.Image, x: int, y: int):
    # file = f"WarpCards/{paste_img}"
    output = Image.open(paste_img).convert('RGBA')
    output = output.resize(size=(525,276))
    output = output.rotate(13, expand=1)

    background.paste(output, (x, y), output)
    return

# WITH THREADING
def ten_pull(imgs: list):
    new = Image.new('RGBA', (2100, 1350), color=0xffffff)
    threads = []

    # Top Left
    thread1 = threading.Thread(target=rotator, args=(imgs[0], new, 0, 250))
    threads.append(thread1)

    # Top Middle
    thread2 = threading.Thread(target=rotator, args=(imgs[1], new, 550, 125))
    threads.append(thread2)

    # Top Right
    thread3 = threading.Thread(target=rotator, args=(imgs[2], new, 1100, -5))
    threads.append(thread3)

    # Middle Left Most
    thread4 = threading.Thread(target=rotator, args=(imgs[3], new, -100, 650))
    threads.append(thread4)

    # Middle 2nd from Left
    thread5 = threading.Thread(target=rotator, args=(imgs[4], new, 450, 525))
    threads.append(thread5)

    # Middle 2nd from Right
    thread6 = threading.Thread(target=rotator, args=(imgs[5], new, 1000, 395))
    threads.append(thread6)

    # Middle Right Most
    thread7 = threading.Thread(target=rotator, args=(imgs[6], new, 1550, 270))
    threads.append(thread7)

    # Bottom Left
    thread8 = threading.Thread(target=rotator, args=(imgs[7], new, 400, 910))
    threads.append(thread8)

    # Bottom Middle
    thread9 = threading.Thread(target=rotator, args=(imgs[8], new, 950, 785))
    threads.append(thread9)

    # Bottom Right
    thread10 = threading.Thread(target=rotator, args=(imgs[9], new, 1500, 660))
    threads.append(thread10)

    for each in threads:
        each.start()
    for thread in threads:
        thread.join()

    # new.show()
    return new


# bg = Image.new('RGBA', (2100, 1350), color=0xffffff)

# while True:
#     lessgo = input("Do you want to Pull? ")
#     if lessgo.lower() == "no" or lessgo.lower() == 'n':
#         break
#     elif lessgo.lower() == "yes" or lessgo.lower() == 'y':
#         selected = randomizer('WarpCards')
#         ten_pull(selected)
#     else:
#         print("Please type 'yes' or 'no'.")


