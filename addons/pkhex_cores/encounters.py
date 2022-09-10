# Handling for the following commands: find, learns
# type: ignore reportMissingImports

import sys
import os
import re
import clr
import numpy

# Import PKHeX stuff
sys.path.append(os.getcwd() + r"/addons/pkhex_cores/deps")
clr.AddReference("PKHeX.Core")
from PKHeX.Core import EncounterLearn, SaveUtil  # Import methods
from PKHeX.Core import Species, Move, GameVersion  # Import Enums
# Import base C# Objects
from System.Collections.Generic import List
from System import Enum


def t():
    return get_moves("Beldum", "6", ["Quick Attack", "Tackle", "Flame Burst", "Hidden Power"])


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


def get_encounters(pokemon, generation, moves: list = None):
    for species in Enum.GetNames(Species):
        if pokemon == species:
            break
    else:
        return 400
    special = generation if generation in ("LGPE", "BDSP", "PLA") else None
    gen = "7" if generation == "LGPE" else "8" if generation in ("BDSP", "PLA") else generation
    moves_csharp_list = List[str]()
    if moves:
        for move in moves:
            moves_csharp_list.Add(move)
    encounters = EncounterLearn.GetLearnSummary(pokemon, moves_csharp_list)
    encounter_type = ""
    genlocs = []
    locations = []
    for encounter in encounters:
        if encounter.startswith("="):
            if len(locations) > 0:
                genlocs.append(
                    {
                        "encounter_type": encounter_type,
                        "location": locations
                    })
            locations = []
            encounter_type = encounter.replace("=", "")
            continue
        reg_gen = get_string_from_regex("Gen[1-9]", encounter)
        if gen not in reg_gen:
            continue
        loc = get_string_from_regex("(?<=.{8}).+?(?=:)", encounter)  # Get location
        games = get_string_from_regex("([\t ][A-Z , a-z 0-9]{1,100}$|Any)", encounter)  # Get games for location
        games = games.replace(" ", "").replace(":", "").strip()
        if not special and any(iter_gen for iter_gen in ("BD", "SP", "PLA", "GG", "GE", "GO", "GP") if iter_gen in (game for game in games.split(','))):
            continue
        if special == "BDSP" and not any(iter_gen for iter_gen in ("BD", "SP") if iter_gen in (game for game in games.split(','))):
            continue
        elif special == "PLA" and "PLA" not in games:
            continue
        elif special == "LGPE" and not any(iter_gen for iter_gen in ("GO", "GG", "GP", "GE") if iter_gen in (game for game in games.split(','))):
            continue
        elif not special and "Gen" in games:
            games = re.sub(",Gen[0-9]{1,2}", "", games)
        games_list = games.split(',')
        locations.append(
            {
                "name": loc,
                "games": games_list
            })
    if len(locations) > 0:  # Add last entry if locations > 0
        genlocs.append(
            {
                "encounter_type": encounter_type,
                "location": locations
            })
    if len(genlocs) == 0:
        return 500
    return genlocs


def get_moves(pokemon, generation, moves: list):
    for species in Enum.GetNames(Species):
        if pokemon == species:
            break
    else:
        return 400
    learnables = []
    for move in moves:
        formatted_move = move.title().replace(" ", "")
        for real_move in Enum.GetNames(Move):
            if formatted_move == real_move:
                break
        else:
            continue
        temp_csharp_list = List[str]()
        temp_csharp_list.Add(formatted_move)
        learnables.append(
            {
                "name": move.title(),
                "learnable": EncounterLearn.CanLearn(pokemon, temp_csharp_list)
            })
    if len(learnables) == 0:
        return 500
    return learnables
