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
from PKHeX.Core import FormConverter, GameInfo, EntityContext, PersonalTable  # Import classes
from PKHeX.Core import Species, GameVersion, Ability  # Import Enums
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
    return get_base_info(mon, form, "7", shiny)


game_version_dict = {
    "1": GameVersion.RBY,
    "2": GameVersion.GSC,
    "3": GameVersion.RSE,
    "4": GameVersion.DPPt,
    "5": GameVersion.B2W2,
    "6": GameVersion.ORAS,
    "7": GameVersion.USUM,
    "8": GameVersion.BDSP,
    "BDSP": GameVersion.BDSP,
    "PLA": GameVersion.PLA,
    "LGPE": GameVersion.GG
}

entity_context_dict = {
    "1": EntityContext.Gen1,
    "2": EntityContext.Gen2,
    "3": EntityContext.Gen3,
    "4": EntityContext.Gen4,
    "5": EntityContext.Gen5,
    "6": EntityContext.Gen6,
    "7": EntityContext.Gen7,
    "8": EntityContext.Gen8,
    "LGPE": EntityContext.Gen7b,
    "BDSP": EntityContext.Gen8a,
    "PLA": EntityContext.Gen8b
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
