"""The GTA Wiki scrambles some 'sensitive' words in its HTML (e.g. 'Assault' -> 'Jbbjduc').
fix() restores the ones we found; scan new data for odd words before publishing (see parse_*.py)."""
import re
FIXES = [("Jbbjduc", "Assault"), ("Fxxfzqy", "Assault"), ("Oggoizh", "Assault"), ("Zaypw Jsbi", "Strip Club"), ("zaypw jsbi", "strip club"),
         ("Dzompcm", "Playboy"), ("zlebhs", "sexual"), ("tlaohtwolahtpul", "methamphetamine"), ("gsl gvcd", "sex shop"),
         ("Sgqcfh", "Escort"), ("Yazuka", "Yakuza")]
def fix(s):
    for a, b in FIXES: s = s.replace(a, b)
    return s
