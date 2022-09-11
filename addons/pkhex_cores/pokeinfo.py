# Handling for the following commands: pokeinfo, qr, forms
# type: ignore reportMissingImports

import sys
import os
import re
import clr
from addons.helper import get_sprite_url, get_string_from_regex

# Import PKHeX stuff
sys.path.append(os.getcwd() + r"/addons/pkhex_cores/deps")
clr.AddReference("PKHeX.Core")
from PKHeX.Core import FormConverter, GameInfo, EntityContext, EntityFormat, EntitySummary, PersonalTable  # Import classes
from PKHeX.Core import Species, GameVersion, Ability  # Import Enums
from PKHeX.Core import PokeList1, PokeList2, PK3, PK4, PK5, PK6, PK7, PB7, PK8, PB8, PA8  # Import PKX classes
# Import base C# Objects
from System import Enum, UInt16, Byte


def t():
    mon = "Pikachu"
    moves = [
        "Follow Me",
        "Quick Attack",
        "Hidden Power"
    ]
    form = None
    shiny = False
    return get_pokemon_file_info(mon, form, "7", shiny)


game_version_dict = {
    "1": GameVersion.RBY,
    "2": GameVersion.GSC,
    "3": GameVersion.RSE,
    "4": GameVersion.DPPt,
    "5": GameVersion.B2W2,
    "6": GameVersion.ORAS,
    "7": GameVersion.USUM,
    "LGPE": GameVersion.GG,
    "8": GameVersion.SWSH,
    "BDSP": GameVersion.BDSP,
    "PLA": GameVersion.PLA,
}

pkx_version_dict = {
    "1": PokeList1,
    "2": PokeList2,
    "3": PK3,
    "4": PK4,
    "5": PK5,
    "6": PK6,
    "7": PK7,
    "LGPE": PB7,
    "8": PK8,
    "BDSP": PB8,
    "PLA": PA8,
}

entity_context_dict = {
    "1": EntityContext.Gen1,
    "2": EntityContext.Gen2,
    "3": EntityContext.Gen3,
    "4": EntityContext.Gen4,
    "5": EntityContext.Gen5,
    "6": EntityContext.Gen6,
    "7": EntityContext.Gen7,
    "LGPE": EntityContext.Gen7b,
    "8": EntityContext.Gen8,
    "BDSP": EntityContext.Gen8a,
    "PLA": EntityContext.Gen8b
}

generation_version_dict = {
    "1": [35, 36, 37, 38, 50, 51, 84, 83],
    "2": [39, 40, 41, 52, 53, 85],
    "3": [1, 2, 3, 4, 5, 54, 55, 56, 57, 58, 59],
    "4": [10, 11, 12, 7, 8, 60, 61, 62, 0x3F],
    "5": [20, 21, 22, 23, 0x40, 65],
    "6": [24, 25, 26, 27, 66, 67, 68],
    "7": [30, 0x1F, 0x20, 33, 69, 70],
    "LGPE": [71, 34, 42, 43],
    "8": [44, 45, 47, 72],
    "BDSP": [73, 48, 49],
    "PLA": [471]
}

pokemon_egg_groups = [
    "Monster",
    "Water 1",
    "Bug",
    "Flying",
    "Field",
    "Fairy",
    "Grass",
    "Human-Like",
    "Water 3",
    "Mineral",
    "Amorphous",
    "Water 2",
    "Ditto",
    "Dragon",
    "Undiscovered"
]

pokemon_colour_index = [
    "Red",
    "Blue",
    "Yellow",
    "Green",
    "Black",
    "Brown",
    "Purple",
    "Gray",
    "White",
    "Pink",
]

pla_species = [
    722, 723, 724, 155, 156, 157, 501, 502, 503, 399, 400, 396, 397, 398, 403, 404, 405, 265, 266, 267,
    268, 269, 77, 78, 133, 134, 135, 136, 196, 197, 470, 471, 700, 41, 42, 169, 425, 426, 401, 402, 418,
    419, 412, 413, 414, 74, 75, 76, 234, 899, 446, 143, 46, 47, 172, 25, 26, 63, 64, 65, 390,
    391, 392, 427, 428, 420, 421, 54, 55, 415, 416, 123, 900, 212, 214, 439, 122, 190, 424, 129, 130,
    422, 423, 211, 904, 440, 113, 242, 406, 315, 407, 455, 548, 549, 114, 465, 339, 340, 453, 454, 280,
    281, 282, 475, 193, 469, 449, 450, 417, 434, 435, 216, 217, 901, 704, 705, 706, 95, 208, 111, 112,
    464, 438, 185, 108, 463, 175, 176, 468, 387, 388, 389, 137, 233, 474, 92, 93, 94, 442, 198, 430,
    201, 363, 364, 365, 223, 224, 451, 452, 58, 59, 431, 432, 66, 67, 68, 441, 355, 356, 477, 393,
    394, 395, 458, 226, 550, 902, 37, 38, 72, 73, 456, 457, 240, 126, 467, 81, 82, 462, 436, 437,
    239, 125, 466, 207, 472, 443, 444, 445, 299, 476, 100, 101, 479, 433, 358, 200, 429, 173, 35, 36,
    215, 903, 461, 361, 362, 478, 408, 409, 410, 411, 220, 221, 473, 712, 713, 459, 570, 571, 672, 628,
    447, 448, 480, 481, 482, 485, 486, 488, 641, 642, 645, 905, 483, 484, 487, 493, 489, 490, 492, 491
]


def form_entry_switcher(csharp_pokemon, csharp_form, generation):
    if generation == "1":
        return PersonalTable.Y.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "2":
        return PersonalTable.C.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "3":
        return PersonalTable.E.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "4":
        return PersonalTable.HGSS.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "5":
        return PersonalTable.B2W2.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "6":
        return PersonalTable.AO.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "7":
        return PersonalTable.USUM.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "LGPE":
        return PersonalTable.GG.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "8":
        return PersonalTable.SWSH.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "BDSP":
        return PersonalTable.BDSP.GetFormEntry(csharp_pokemon, csharp_form)
    elif generation == "PLA":
        return PersonalTable.LA.GetFormEntry(csharp_pokemon, csharp_form)
    else:
        return 400


def get_pokemon_forms(pokemon, generation: str = "8"):
    pokemon_id = [int(item) for item in Enum.GetValues(Species) if Enum.GetName(Species, item) == pokemon]
    if len(pokemon_id) == 0:
        return 400
    csharp_pokemon = UInt16(pokemon_id[0])
    game_info_strings = GameInfo.Strings
    if pokemon == "Alcremie":
        forms = FormConverter.GetAlcremieFormList(game_info_strings.forms)
    else:
        forms = FormConverter.GetFormList(csharp_pokemon, game_info_strings.Types, game_info_strings.forms, GameInfo.GenderSymbolASCII, entity_context_dict[generation])
    return [form for form in forms]


def get_base_info(pokemon, form, generation: str, shiny: bool = False):
    if pokemon.lower() in ('jangmo', 'hakamo', 'kommo') and species_form_pair[1] == "o":
        pokemon += '-o'
        species_form_pair.pop(1)
    elif pokemon.lower() == "ho" and species_form_pair[1] == "oh":
        pokemon = "ho-oh"
        species_form_pair.pop(1)
    elif pokemon.lower() == "porygon" and species_form_pair[1].lower() == "z":
        pokemon = "porygon-z"
        species_form_pair.pop(1)
    pokemon_id = [int(item) for item in Enum.GetValues(Species) if Enum.GetName(Species, item) == pokemon]
    if len(pokemon_id) == 0:
        return 400
    csharp_pokemon = UInt16(pokemon_id[0])
    csharp_form_num = Byte(0)
    game_info_strings = GameInfo.Strings
    if form is not None:
        forms = FormConverter.GetFormList(csharp_pokemon, game_info_strings.Types, game_info_strings.forms, GameInfo.GenderSymbolASCII, entity_context_dict[generation])
        try:
            form_num = forms.index(form)
        except ValueError:
            return 400
        if form_num >= 0 or form_num < len([csharp_form for csharp_form in forms]):
            csharp_form_num = Byte(form_num)
    pokemon_info = form_entry_switcher(csharp_pokemon, csharp_form_num, generation)
    if pokemon_info == 400:
        return 400
    types = [game_info_strings.types[pokemon_info.Type1]]
    types.append(game_info_strings.types[pokemon_info.Type2]) if pokemon_info.Type2 != -1 and pokemon_info.Type2 != pokemon_info.Type1 else types.append(None)
    groups = []
    groups.append(pokemon_egg_groups[pokemon_info.EggGroup1 - 1]) if pokemon_info.EggGroup1 != -1 else types.append(None)
    groups.append(pokemon_egg_groups[pokemon_info.EggGroup2 - 1]) if pokemon_info.EggGroup2 != -1 and pokemon_info.EggGroup2 != pokemon_info.EggGroup1 else types.append(None)
    sprite_url = get_sprite_url(str(pokemon_id[0]), generation, form.lower() if form else form, shiny, "F" if pokemon_info.Gender == 1 else "M" if pokemon_info.Gender == 0 else "-", pokemon.lower())
    base_pokemon = {
        "hp": pokemon_info.HP,
        "atk": pokemon_info.ATK,
        "def": pokemon_info.DEF,
        "spe": pokemon_info.SPE,
        "spa": pokemon_info.SPA,
        "spd": pokemon_info.SPD,
        "catch_rate": pokemon_info.CatchRate,
        "evo_stage": pokemon_info.EvoStage,
        "gender": pokemon_info.Gender,
        "hatch_cycles": pokemon_info.HatchCycles,
        "base_friendship": pokemon_info.BaseFriendship,
        "exp_growth": pokemon_info.EXPGrowth,
        "ability1": Enum.GetName(Ability, UInt16(pokemon_info.Ability1)),
        "ability2": Enum.GetName(Ability, UInt16(pokemon_info.Ability2)),
        "ability_h": Enum.GetName(Ability, UInt16(pokemon_info.AbilityH)) if hasattr(pokemon_info, "AbilityH") else None,
        "colour": pokemon_colour_index[pokemon_info.Color],
        "height": pokemon_info.Height,
        "weight": pokemon_info.Weight,
        "types": types,
        "egg_groups": groups,
        "is_dual_gender": True if pokemon_info.OnlyMale == pokemon_info.OnlyFemale else False,
        "is_genderless": pokemon_info.Genderless,
        "only_female": pokemon_info.OnlyFemale,
        "bst": (pokemon_info.ATK + pokemon_info.DEF + pokemon_info.SPE + pokemon_info.SPA + pokemon_info.SPD + pokemon_info.HP),
        "species_sprite_url": sprite_url
    }
    return base_pokemon


def get_pokemon_file_info(file):
    pokemon = EntityFormat.GetFromBytes(file)
    for key, value in generation_version_dict.items():
        if pokemon.Version in value:
            generation = key
            break
    if generation in ("1", "2"):
        pokemon = pkx_version_dict[generation](file)[0]
    else:
        pokemon = pkx_version_dict[generation](file)
    if pokemon.Species <= 0 or ((generation == "1" and pokemon.Species > 151) or (generation == "2" and pokemon.Species > 251) or (generation == "3" and pokemon.Species > 386) or (generation in ("4", "BDSP") and pokemon.Species > 493) or (generation == "5" and pokemon.Species > 649) or (generation == "6" and pokemon.Species > 721) or (generation == "7" and pokemon.Species > 809) or (generation == "LGPE" and pokemon.Species > 251 and pokemon.Species not in (808, 809)) or (generation == "8" and pokemon.Species > 896) or (generation == "PLA" and pokemon.Species not in pla_species)):
        return 500
    game_info_strings = GameInfo.Strings
    entity_summary = EntitySummary(pokemon, game_info_strings)
    moves = [
        entity_summary.Move1,
        entity_summary.Move2,
        entity_summary.Move3,
        entity_summary.Move4
    ]
    stats = [
        {"iv": entity_summary.HP_IV, "ev": entity_summary.HP_EV, "total": entity_summary.HP},
        {"iv": entity_summary.ATK_IV, "ev": entity_summary.ATK_EV, "total": entity_summary.ATK},
        {"iv": entity_summary.DEF_IV, "ev": entity_summary.DEF_EV, "total": entity_summary.DEF},
        {"iv": entity_summary.SPA_IV, "ev": entity_summary.SPA_EV, "total": entity_summary.SPA},
        {"iv": entity_summary.SPD_IV, "ev": entity_summary.SPD_EV, "total": entity_summary.SPD},
        {"iv": entity_summary.SPE_IV, "ev": entity_summary.SPE_EV, "total": entity_summary.SPE}
    ]
    form_value = entity_summary.Form
    if entity_summary.Form != 0:
        forms = FormConverter.GetFormList(pokemon.Species, game_info_strings.Types, game_info_strings.forms, GameInfo.GenderSymbolASCII, entity_context_dict[generation])
        form_value = forms[form_value]
    sprite_url = get_sprite_url(str(pokemon.Species), generation, form_value.lower(), entity_summary.IsShiny, entity_summary.Gender, entity_summary.Species.lower())
    pokemon_info = {
        "species": entity_summary.Species,
        "nickname": entity_summary.Nickname,
        "gender": entity_summary.Gender,
        "level": entity_summary.Level,
        "nature": entity_summary.Nature,
        "generation": generation,
        "ability": entity_summary.Ability if hasattr(entity_summary, "Ability") else "N/A",
        "ot": entity_summary.OT,
        "sid": entity_summary.SID,
        "tid": entity_summary.TID,
        "ht": pokemon.HT_Name if hasattr(pokemon, "HT_Name") and pokemon.HT_Name != "" else "N/A",
        "met_loc": entity_summary.MetLoc,
        "version": entity_summary.Version,
        "ball": entity_summary.Ball,
        "held_item": entity_summary.HeldItem,
        "stats": stats,
        "moves": moves,
        "species_sprite_url": sprite_url,
        "is_legal": True if entity_summary.Legal == "-" else False
    }
    return pokemon_info
