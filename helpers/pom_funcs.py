from difflib import SequenceMatcher
from poms.pom_misc import combat_emojis
import json

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

with open('data/characters.json', 'r') as f:
    chara_file = json.load(f)
with open('data/relics.json', 'r') as f:
    relics = json.load(f)
with open('data/light_cones.json', 'r') as f:
    light_cones = json.load(f)
with open('data/best_light_cones.json', 'r') as f:
    best_light_cones = json.load(f)
with open('data/eidolons.json', 'r') as f:
    eidolons = json.load(f)
