# Handling for the following commands: find, learns

import sys
import os
import re
import clr
import numpy

sys.path.append(os.getcwd() + r"\\addons\\pkhex_cores\\deps")
clr.AddReference("PKHeX.Core.AutoMod")
from PKHeX.Core import EncounterLearn, Species  # type: ignore
from System.Collections.Generic import List  # type: ignore
from System import Enum  # type: ignore


def get_string_from_regex(regex_pattern, data):
    match = re.search(regex_pattern, data)
    if match:
        return match.group(0)  # Return entire match
    return ""  # Handle failed matches by returning an empty string


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
