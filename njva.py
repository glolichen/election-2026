from all import *

VA_PRES = {
    2024: 5.78,
    2020: 10.11,
    2016: 5.32,
    2012: 3.88,
    2008: 6.3,
    2004: -8.2,
	2000: -8.03,
	1996: -1.95,
	1992: -4.38,
	1988: -20.51,
}
VA_GOV = {
    2025: 15.4,
    2021: -2.0,
    2017: 8.9,
    2013: 2.6,
    2009: -17.3,
	2005: 5.7,
	2001: 5.2,
	1997: -13.2,
	1993: -17.4,
}

NJ_PRES = {
    2024: 5.91,
    2020: 15.88,
    2016: 13.77,
    2012: 17.79,
    2008: 15.57,
    2004: 6.69,
	2000: 15.84,
	1996: 17.86,
	1992: 2.37,
	1988: -13.64,
}

NJ_GOV = {
    2025: 14.3,
    2021: 3.2,
    2017: 14.1,
    2013: -22,
    2009: -3.5,
	2005: 10.5,
	2001: 14.7,
	1997: -1.1,
	1993: -1.0,
}



def pvi(results):
    pvis = {}
    for year in PRES_YEARS:
        pvis[year] = results[year] * 0.67 + \
                    results[year - 4] * 0.33
    return pvis

def nj_va():
    nj_pvi, va_pvi = pvi(NJ_PRES), pvi(VA_PRES)

    # print(nj_pvi)
    # print(va_pvi)

    nj_swing, va_swing = {}, {}

    for year in PRES_YEARS:
        gov_margin = NJ_GOV[year + 1]
        nj_swing[year+2] = gov_margin - nj_pvi[year]

        gov_margin = VA_GOV[year + 1]
        va_swing[year+2] = gov_margin - va_pvi[year]

    # print(nj_swing)

    return nj_swing, va_swing

if __name__ == "__main__":
    print(nj_va())