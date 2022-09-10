# Handling for the following commands: pokeinfo, qr, forms
# type: ignore reportMissingImports

import sys
import os
import re
import clr
import numpy

# Import PKHeX stuff
sys.path.append(os.getcwd() + r"/addons/pkhex_cores/deps")
clr.AddReference("PKHeX.Core")
from PKHeX.Core import FormConverter, GameInfo, EntityContext  # Import classes
from PKHeX.Core import Species, GameVersion  # Import Enums
# Import base C# Objects
from System import Enum, UInt16


def t():
    mon = "Pikachu"
    moves = [
        "Follow Me",
        "Quick Attack",
        "Hidden Power"
    ]
    return get_pokemon_forms(mon)


def get_string_from_regex(regex_pattern, data):
    match = re.search(regex_pattern, data)
    if match:
        return match.group(0)  # Return entire match
    return ""  # Handle failed matches by returning an empty string


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


def get_pokemon_forms(pokemon):
    pokemon_id = [int(item) for item in Enum.GetValues(Species) if Enum.GetName(Species, item) == pokemon]
    if len(pokemon_id) == 0:
        return 400
    csharp_pokemon = UInt16(pokemon_id[0])
    game_info_strings = GameInfo.Strings
    if pokemon == "Alcremie":
        forms = FormConverter.GetAlcremieFormList(game_info_strings.forms)
    else:
        forms = FormConverter.GetFormList(csharp_pokemon, game_info_strings.Types, game_info_strings.forms, GameInfo.GenderSymbolASCII, EntityContext.Gen8)
    return [form for form in forms]
