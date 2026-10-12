"""AUT-35a: the derived counts quoted in 70_massivesteps_validation.md.

Every aggregate in that report comes from here rather than from prose arithmetic
(AGENT_GUARDRAILS N2: agents quote, they do not compute). The per-year inputs are
the verbatim histograms printed by aut35a_window.py and aut35a_yelp_checkin_scan.py;
this script only sums and divides them.

Run: python3 aut35a_derived_counts.py
"""

# aut35a_window.py timestamp <the three Massive-STEPS-Istanbul raw parquet files>
UPSTREAM = {"2012": 198108, "2013": 203042, "2017": 60327, "2018": 82994}

# aut35a_window.py datetime output/check2hgi/istanbul/chrono_split/split_assignment.parquet
MODELED = {"2012": 160601, "2013": 166641, "2017": 56797, "2018": 78576}

# aut35a_yelp_checkin_scan.py 9000000000  (YEARS=... line)
YELP = {"2009": 2, "2010": 209154, "2011": 901460, "2012": 1289505, "2013": 1552816,
        "2014": 1625890, "2015": 1709865, "2016": 1554780, "2017": 1348470,
        "2018": 1157260, "2019": 1035165, "2020": 474174, "2021": 477474,
        "2022": 20940}

OLD = ("2012", "2013")
NEW = ("2017", "2018")


def block(d, keys):
    return sum(d[k] for k in keys)


for label, d in (("upstream Istanbul (as distributed)", UPSTREAM),
                 ("modeled Istanbul (chrono split)", MODELED)):
    old = block(d, OLD)
    new = block(d, NEW)
    tot = sum(d.values())
    print(label)
    print("  total=" + str(tot))
    print("  2012+2013=" + str(old) + "  (" + format(100.0 * old / tot, ".1f") + "%)")
    print("  2017+2018=" + str(new) + "  (" + format(100.0 * new / tot, ".1f") + "%)")
    gap = [y for y in ("2014", "2015", "2016") if d.get(y)]
    print("  years present in 2014-2016: " + (repr(gap) if gap else "none"))

post = sum(v for k, v in YELP.items() if k >= "2019")
print("Yelp checkin.json timestamps in 2019 or later=" + str(post))
print("Yelp total timestamps scanned=" + str(sum(YELP.values())))
