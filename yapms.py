import json

GEN_BALLOT = 8.53

with open("yapmsbase.json", "r") as file:
    yapms = json.load(file)

with open("cpvi2026.csv", "r") as file:
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

cpvi = {}
for line in lines:
    line = line.rstrip("\n")
    split = line.split(",")

    margin = GEN_BALLOT + float(split[1]) * 2
    is_rep = margin < 0
    marginabs = abs(margin)

    is_cur_rep = split[2] == "R"

    if is_rep != is_cur_rep:
        current = "R" if is_cur_rep else "D"
        next = "R" if is_rep else "D"
        print(f"Flip! {split[0]}, {current}->{next}, {margin:.1f}")

    margin_num = 0
    if marginabs <= 2:
        margin_num = 3
    elif marginabs <= 5:
        margin_num = 2
    elif marginabs <= 12:
        margin_num = 1

    set_map(split[0], is_rep, margin_num)
    
with open("yapmsout.json", "w", encoding="utf-8") as file:
    json.dump(yapms, file)

