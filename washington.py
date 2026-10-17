# note: redistricting is accounted for
#  - ***2 presidential and ***4 midterm use the same districts
#  - ***0 presidential and ***2 midterm do NOT use the same districts
#  - all others use the same districts
# problems are 2020/2022 and 2000/2002
# 2022 is fine because presidential data after 2008 uses new districts
# Unfortunately I cannot find 2000 results on 2002 districts
# The districts changed very little so the effect should not be large

from scipy import stats
from all import *
import districtpvi

class DistrictVotes:
    def __init__(self):
        self.dem = 0
        self.rep = 0
        self.total = 0
    def __repr__(self):
        return f"(D: {self.dem}, R: {self.rep}, Total: {self.total})"

def wa_primary():
    with open("wa/allwa.csv", "r") as file:
        lines = file.readlines()

    dvotes, districts = {}, {}
    for year in range(1994, 2026+1, 4):
        dvotes[year], districts[year] = {}, {}

    for line in lines:
        line = line.rstrip("\n")
        split = line.split(",")
        year = int(split[0])
        district = int(split[1])
        party = split[2].lower()
        votes = int(split[3])

        if district not in dvotes[year]:
            dvotes[year][district] = DistrictVotes()

        dvotes[year][district].total += votes
        if "democrat" in party:
            dvotes[year][district].dem += votes
        if "republican" in party:
            dvotes[year][district].rep += votes

    pvis = districtpvi.pvi()
    for year in range(1994, 2026+1, 4):
        swings = []
        for seat, votes in dvotes[year].items():
            dem_pct = votes.dem / votes.total * 100
            rep_pct = votes.rep / votes.total * 100
            margin = dem_pct - rep_pct

            seat_name = f"WA-{seat:02d}"
            pvi = pvis[year - 2][seat_name]

            # print(year, seat_name, margin, pvi)

            swing = margin - pvi

            swings.append(swing)

        districts[year] = float(stats.trim_mean(swings, SPECIALS_TRIM_MEAN_PROP))

    return districts

if __name__ == "__main__":
    print(wa_primary())