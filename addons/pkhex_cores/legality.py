# Handling for the following commands: legality, legalize
# type: ignore reportMissingImports

import sys
import os
import clr
from addons.helper import get_sprite_url
import addons.pkhex_cores.pkhex_helper as pkhex_helper

# Import PKHeX stuff
sys.path.append(os.getcwd() + r"/addons/pkhex_cores/deps")
clr.AddReference("PKHeX.Core")
from PKHeX.Core import EntityFormat, LegalityAnalysis, LegalityFormatting, EncounterEvent, RibbonStrings, GameInfo  # Import classes
from PKHeX.Core import Species, Ability  # Import Enums
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
    # return get_pokemon_file_info(mon, form, "7", shiny)


def get_legality_report(file):
    EncounterEvent.RefreshMGDB("")
    RibbonStrings.ResetDictionary(GameInfo.Strings.ribbons)
    pokemon = EntityFormat.GetFromBytes(file)
    for key, value in pkhex_helper.generation_version_dict.items():
        if pokemon.Version in value:
            generation = key
            break
    if generation in ("1", "2"):
        pokemon = pkhex_helper.pkx_version_dict[generation](file)[0]
    else:
        pokemon = pkhex_helper.pkx_version_dict[generation](file)
    if pokemon.Species <= 0 or ((generation == "1" and pokemon.Species > 151) or (generation == "2" and pokemon.Species > 251) or (generation == "3" and pokemon.Species > 386) or (generation in ("4", "BDSP") and pokemon.Species > 493) or (generation == "5" and pokemon.Species > 649) or (generation == "6" and pokemon.Species > 721) or (generation == "7" and pokemon.Species > 809) or (generation == "LGPE" and pokemon.Species > 251 and pokemon.Species not in (808, 809)) or (generation == "8" and pokemon.Species > 896) or (generation == "PLA" and pokemon.Species not in pkhex_helper.pla_species)):
        return 500
    analysis = LegalityAnalysis(pokemon)
    report = LegalityFormatting.Report(analysis)
    if report == "Legal!":
        return 200
    elif report == "Analysis not available for this Pokémon.":
        return 201
    return report.replace('\r', '').split('\n')
