from all import *

def pvi():
    # dictionary: year -> (dictionary of CD name -> PVI)
    pvis = {}

    for year in PRES_YEARS:
        pvis[year] = {}

    # 2008-2024: have full district data
    for year in range(2008, 2025, 4):
        syear = str(year)[-2:]
        year_prev = str(year - 4)[-2:]
        
        with open(f"pres/{syear}-{syear}_{year_prev}.csv", "r") as file:
            lines = file.readlines()

        for line in lines:
            if line == lines[0]: continue

            line = line.rstrip("\n")
            split = line.split(",")

            cur_pvi = 0
            
            pres_d = float(split[1])
            pres_r = float(split[2])        
            if split[3] == "" or split[4] == "":
                cur_pvi = pres_d - pres_r
            else:
                pres_d_prev = float(split[3])
                pres_r_prev = float(split[4])
                cur_pvi = (pres_d - pres_r) * PVI_PRES_WEIGHT_SAME + \
                    (pres_d_prev - pres_r_prev) * PVI_PRES_WEIGHT_PREV

            # print(split)

            pvis[year][split[0]] = cur_pvi

    # 2004 and before: constructed manually :(
    # I was too lazy so no weighting
    with open("pres/92-04special.csv", "r") as file:
        speical_lines = file.readlines()
    with open("pres/92-04wa.csv", "r") as file:
        wa_lines = file.readlines()

    lines = [*speical_lines, *wa_lines]

    for line in lines:
        line = line.rstrip("\n")
        split = line.split(",")
        district = split[0]
        year = int(split[1])
        # print(year)
        pvis[year][district] = float(split[2])

    return pvis

if __name__ == "__main__":
    print(pvi())