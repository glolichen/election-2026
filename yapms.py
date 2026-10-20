import json
import districtpvi

# First calculate candidate overperformances in 2024
# need 2024 district PVI
GEN_BALLOT = 4.3

retiring, freshmen, open_seat, uncontested = set(), set(), set(), set()
with open("2026retirement.csv", "r") as file:
    lines = file.readlines()
    for line in lines:
        retiring.add(line.rstrip("\n"))
with open("2026open.csv", "r") as file:
    lines = file.readlines()
    for line in lines:
        open_seat.add(line.rstrip("\n"))
with open("2026freshmen.csv", "r") as file:
    lines = file.readlines()
    for line in lines:
        freshmen.add(line.rstrip("\n"))
with open("2024uncontested.csv", "r") as file:
    lines = file.readlines()
    for line in lines:
        uncontested.add(line.rstrip("\n"))

with open("2024house.csv", "r") as file:
    lines = file.readlines()

# + value = { overperforming D, underperforming R }
# calculated by: house margin - "li pvi"
overperformance = {}

# this is on 2024 CD's, as we want
li_pvi = districtpvi.pvi()

for line in lines:
    line = line.rstrip("\n")
    split = line.split(",")

    if split[1] == "AL":
        district0 = district = f"{split[0]}-{split[1]}"
    else:
        if len(split[1]) == 1:
            district = f"{split[0]}-{split[1]}"
            district0 = f"{split[0]}-{int(split[1]):02}"
        else:
            district0 = district = f"{split[0]}-{split[1]}"

    party = split[2].lower()
    pct = int(split[3]) / int(split[4]) * 100

    if district not in overperformance:
        overperformance[district] = -li_pvi[2024][district0]

    # 1. electoral fusion
    # 2. "democratic-farmer-labor" and "democratic-nonpartisan league"
    # thanks, new york, minnesota and north dakota!
    if "democrat" in party or "working families" in party:
        overperformance[district] += pct
    if "republican" in party or "conservative" in party:
        overperformance[district] -= pct

# print(overperformance)

with open("yapmsbase.json", "r") as file:
    yapms = json.load(file)

with open("2026cpvi.csv", "r") as file:
    lines = file.readlines()

# 0 = safe, 1 = likely, etc
def set_map(id: str, is_rep: bool, margin: int):
    for district in yapms["regions"]:
        if district["id"] != id:
            continue
        candidate = district["candidates"][0]
        candidate["id"] = "1" if is_rep else "0"
        candidate["margin"] = margin
        
        # print(district)

def margin_to_str(margin: float):
    party = "D" if margin >= 0 else "R"
    return f"{party}+{abs(margin):.1f}"

cpvi = {}
for line in lines:
    line = line.rstrip("\n")
    split = line.split(",")

    district = split[0]

    margin = GEN_BALLOT + float(split[1]) * 2

    is_retire = district in retiring
    is_open = district in open_seat
    is_freshman = district in freshmen

    if not (is_retire or is_open or is_freshman):
        margin += 0.5 * overperformance[district]

    is_rep = margin < 0
    marginabs = abs(margin)

    is_cur_rep = split[2] == "R"

    if is_rep != is_cur_rep:
        current = "R" if is_cur_rep else "D"
        next = "R" if is_rep else "D"
        note = ""
        if is_open: note = "OPEN"
        elif is_retire: note = "RETIRING"

        # print(f"|{district}|  {note}  |{current}|{next}|{margin_to_str(margin)}|")

    margin_num = 0
    if marginabs <= 2:
        margin_num = 3
        print(f"|{district}|    |    |{margin_to_str(margin)}|")
    elif marginabs <= 5:
        margin_num = 2
    elif marginabs <= 12:
        margin_num = 1

    set_map(district, is_rep, margin_num)
    
with open("yapmsout.json", "w", encoding="utf-8") as file:
    json.dump(yapms, file)

