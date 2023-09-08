from difflib import SequenceMatcher
import json
import math
from helpers.pom_misc import combat_emojis


def seperate_lcs(lcs):
    """
    Seperates all the light cones into a dictionary, with each Path as key and the list of Cones of that path as it's value

    Returns a ``dict``
    """
    paths = {
    'The Destruction' : [],
    'The Abundance' : [],
    'The Hunt' : [],
    'The Nihility' : [],
    'The Erudition' : [],
    'The Preservation' : [],
    'The Harmony' : []
    }
    for cone in lcs:
        cone_path = (' ').join(cone['path'].split()[0:2])
        paths[cone_path].append(cone['name'])

    return paths

def seperate_charas(charas):
    """
    Seperates all the characters into a dictionary, with each Path as key and the list of Characters of the respective path as it's value

    Returns a ``dict``
    """
    paths = {
    'The Destruction' : [],
    'The Abundance' : [],
    'The Hunt' : [],
    'The Nihility' : [],
    'The Erudition' : [],
    'The Preservation' : [],
    'The Harmony' : []
    }

    for chara_info in charas:
        paths[chara_info['path']].append(f"{chara_info['name']} {combat_emojis[chara_info['combat']]}")

    return paths

def similar(a, b):
    """
    Similarity check between ``a`` and ``b``. Returns a ratio (Float).
    """
    return SequenceMatcher(None, a, b).ratio()

def similarity_sorter(search_results, keyword):
    """
    Sorts the search results based on the similarity between it and the keyword.
    ### Parameters
    ``search_results``: sequence
        A non-empty sequence of search results. \n
    ``keyword``: str
        The term you want to search. \n
    Returns the sorted list.
    """
    temp_listed_results = []
    for result in search_results:
        x = similar(keyword, result)
        temp_listed_results.append((x, result))

    temp_listed_results.sort(reverse=True)
    sorted_results = [x[1] for x in temp_listed_results]

    return sorted_results

def level_calculator(exp: int):
    """
    Calculate the user's current level based on their current `exp`

    Returns the level as a `float`
    """
    # +1 at the end because I don't want users to start from level 0
    return (((-100) + math.sqrt((100**2) - (-4*25*exp))) / (2*25)) + 1

def exp_required_calculator(level: int):
    """
    Returns the Exp required to reach a certain `level` as an `int`.
    """
    level = int(level - 1)
    return (25*(level**2)) + (100*level)

async def find_from_db(collection, user_id: int):
    """
    - `collection`: A pymongo Collection
    - `user_id`: The user's Discord ID ("_id" in the Collection)

    Finds the user's data from the Collection. If there is no data of that user, creates a new document in the Collection.
    Returns the user's data from the Collection.
    """
    filter = {'_id': user_id}
    if await collection.find_one(filter) == None:
        new_user = {"_id": user_id, "ten_pulls": 0, "characters": {}, "uid": 0, "exp": 0}
        await collection.insert_one(new_user)
    return await collection.find_one(filter)

# JSON File Handling
with open('data/characters.json', 'r', encoding='utf-8') as f:
    chara_file = json.load(f)
with open('data/relics.json', 'r') as f:
    relics = json.load(f)
with open('data/light_cones.json', 'r') as f:
    light_cones = json.load(f)
with open('data/best_light_cones.json', 'r') as f:
    best_light_cones = json.load(f)
with open('data/eidolons.json', 'r') as f:
    eidolons = json.load(f)
with open('warps/data/all_warps.json', 'r') as f:
    all_warp_details: dict = json.load(f)
with open('warps/data/standard_banner.json', 'r') as f:
    standard_warps: dict = json.load(f)
