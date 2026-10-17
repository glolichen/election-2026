# Convention: + = for D, - = for R

from typing import NamedTuple
from scipy import stats

from all import *
import districtpvi

# class District(NamedTuple):
#     # ex. "NJ-03"
#     name: str
#     # weighted average of presidential result and previous presidential election
#     pvi: float

def specials():
    pvis = districtpvi.pvi()

    with open("specials.csv", "r") as file:
        lines = file.readlines()

    # special elections to Congress elected in x year
    specials = {}
    for year in PRES_YEARS:
        specials[year] = []

        
    # print(pvis[2024]["WA-01"])

    for line in lines:
        line = line.rstrip("\n")
        split = line.split(",")

        district, date, win, second = \
            split[0], split[3], split[4], split[6]

        # discard single party races and unserious (non D/R) challengers
        # there are no wins from party other than D or R
        if win == second or (second not in ["D", "R"]):
            continue

        prev_year, margin = int(split[1]), float(split[5])
        margin = margin * (1 if win == "D" else -1)

        pvi = pvis[prev_year][district]

        swing = margin - pvi

        specials[prev_year].append(swing)

        # print(f"{district} ({date}), pvi: {pvi}, margin: {margin}, swing = {swing}")

    # print(specials)
    
    # mean them
    specials_mean = {}
    for year in PRES_YEARS:
        specials_mean[year + 2] = float(stats.trim_mean(specials[year], SPECIALS_TRIM_MEAN_PROP))

    return specials_mean

if __name__ == "__main__":
    print(specials())
