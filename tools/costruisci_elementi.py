#!/usr/bin/env python3
"""
Costruisce dati/elementi.json (118 elementi).

Si lancia una volta sola; il file prodotto e' versionato nel repo.
La configurazione elettronica e' calcolata con l'ordine di riempimento (Aufbau)
e poi corretta a mano per le eccezioni note.

    python3 tools/costruisci_elementi.py
"""

import json
import os

# n, simbolo, nome italiano, massa atomica, categoria, colonna, riga
BASE = [
    (1, "H", "Idrogeno", 1.008, "non-metallo", 1, 1),
    (2, "He", "Elio", 4.003, "gas-nobile", 18, 1),
    (3, "Li", "Litio", 6.94, "alcalino", 1, 2),
    (4, "Be", "Berillio", 9.012, "alcalino-terroso", 2, 2),
    (5, "B", "Boro", 10.81, "semimetallo", 13, 2),
    (6, "C", "Carbonio", 12.011, "non-metallo", 14, 2),
    (7, "N", "Azoto", 14.007, "non-metallo", 15, 2),
    (8, "O", "Ossigeno", 15.999, "non-metallo", 16, 2),
    (9, "F", "Fluoro", 18.998, "alogeno", 17, 2),
    (10, "Ne", "Neon", 20.180, "gas-nobile", 18, 2),
    (11, "Na", "Sodio", 22.990, "alcalino", 1, 3),
    (12, "Mg", "Magnesio", 24.305, "alcalino-terroso", 2, 3),
    (13, "Al", "Alluminio", 26.982, "metallo", 13, 3),
    (14, "Si", "Silicio", 28.085, "semimetallo", 14, 3),
    (15, "P", "Fosforo", 30.974, "non-metallo", 15, 3),
    (16, "S", "Zolfo", 32.06, "non-metallo", 16, 3),
    (17, "Cl", "Cloro", 35.45, "alogeno", 17, 3),
    (18, "Ar", "Argon", 39.948, "gas-nobile", 18, 3),
    (19, "K", "Potassio", 39.098, "alcalino", 1, 4),
    (20, "Ca", "Calcio", 40.078, "alcalino-terroso", 2, 4),
    (21, "Sc", "Scandio", 44.956, "transizione", 3, 4),
    (22, "Ti", "Titanio", 47.867, "transizione", 4, 4),
    (23, "V", "Vanadio", 50.942, "transizione", 5, 4),
    (24, "Cr", "Cromo", 51.996, "transizione", 6, 4),
    (25, "Mn", "Manganese", 54.938, "transizione", 7, 4),
    (26, "Fe", "Ferro", 55.845, "transizione", 8, 4),
    (27, "Co", "Cobalto", 58.933, "transizione", 9, 4),
    (28, "Ni", "Nichel", 58.693, "transizione", 10, 4),
    (29, "Cu", "Rame", 63.546, "transizione", 11, 4),
    (30, "Zn", "Zinco", 65.38, "transizione", 12, 4),
    (31, "Ga", "Gallio", 69.723, "metallo", 13, 4),
    (32, "Ge", "Germanio", 72.630, "semimetallo", 14, 4),
    (33, "As", "Arsenico", 74.922, "semimetallo", 15, 4),
    (34, "Se", "Selenio", 78.971, "non-metallo", 16, 4),
    (35, "Br", "Bromo", 79.904, "alogeno", 17, 4),
    (36, "Kr", "Kripton", 83.798, "gas-nobile", 18, 4),
    (37, "Rb", "Rubidio", 85.468, "alcalino", 1, 5),
    (38, "Sr", "Stronzio", 87.62, "alcalino-terroso", 2, 5),
    (39, "Y", "Ittrio", 88.906, "transizione", 3, 5),
    (40, "Zr", "Zirconio", 91.224, "transizione", 4, 5),
    (41, "Nb", "Niobio", 92.906, "transizione", 5, 5),
    (42, "Mo", "Molibdeno", 95.95, "transizione", 6, 5),
    (43, "Tc", "Tecnezio", 98.0, "transizione", 7, 5),
    (44, "Ru", "Rutenio", 101.07, "transizione", 8, 5),
    (45, "Rh", "Rodio", 102.906, "transizione", 9, 5),
    (46, "Pd", "Palladio", 106.42, "transizione", 10, 5),
    (47, "Ag", "Argento", 107.868, "transizione", 11, 5),
    (48, "Cd", "Cadmio", 112.414, "transizione", 12, 5),
    (49, "In", "Indio", 114.818, "metallo", 13, 5),
    (50, "Sn", "Stagno", 118.710, "metallo", 14, 5),
    (51, "Sb", "Antimonio", 121.760, "semimetallo", 15, 5),
    (52, "Te", "Tellurio", 127.60, "semimetallo", 16, 5),
    (53, "I", "Iodio", 126.904, "alogeno", 17, 5),
    (54, "Xe", "Xeno", 131.293, "gas-nobile", 18, 5),
    (55, "Cs", "Cesio", 132.905, "alcalino", 1, 6),
    (56, "Ba", "Bario", 137.327, "alcalino-terroso", 2, 6),
    (57, "La", "Lantanio", 138.905, "lantanide", 3, 9),
    (58, "Ce", "Cerio", 140.116, "lantanide", 4, 9),
    (59, "Pr", "Praseodimio", 140.908, "lantanide", 5, 9),
    (60, "Nd", "Neodimio", 144.242, "lantanide", 6, 9),
    (61, "Pm", "Promezio", 145.0, "lantanide", 7, 9),
    (62, "Sm", "Samario", 150.36, "lantanide", 8, 9),
    (63, "Eu", "Europio", 151.964, "lantanide", 9, 9),
    (64, "Gd", "Gadolinio", 157.25, "lantanide", 10, 9),
    (65, "Tb", "Terbio", 158.925, "lantanide", 11, 9),
    (66, "Dy", "Disprosio", 162.500, "lantanide", 12, 9),
    (67, "Ho", "Olmio", 164.930, "lantanide", 13, 9),
    (68, "Er", "Erbio", 167.259, "lantanide", 14, 9),
    (69, "Tm", "Tulio", 168.934, "lantanide", 15, 9),
    (70, "Yb", "Itterbio", 173.045, "lantanide", 16, 9),
    (71, "Lu", "Lutezio", 174.967, "lantanide", 17, 9),
    (72, "Hf", "Afnio", 178.49, "transizione", 4, 6),
    (73, "Ta", "Tantalio", 180.948, "transizione", 5, 6),
    (74, "W", "Tungsteno", 183.84, "transizione", 6, 6),
    (75, "Re", "Renio", 186.207, "transizione", 7, 6),
    (76, "Os", "Osmio", 190.23, "transizione", 8, 6),
    (77, "Ir", "Iridio", 192.217, "transizione", 9, 6),
    (78, "Pt", "Platino", 195.084, "transizione", 10, 6),
    (79, "Au", "Oro", 196.967, "transizione", 11, 6),
    (80, "Hg", "Mercurio", 200.592, "transizione", 12, 6),
    (81, "Tl", "Tallio", 204.38, "metallo", 13, 6),
    (82, "Pb", "Piombo", 207.2, "metallo", 14, 6),
    (83, "Bi", "Bismuto", 208.980, "metallo", 15, 6),
    (84, "Po", "Polonio", 209.0, "semimetallo", 16, 6),
    (85, "At", "Astato", 210.0, "alogeno", 17, 6),
    (86, "Rn", "Radon", 222.0, "gas-nobile", 18, 6),
    (87, "Fr", "Francio", 223.0, "alcalino", 1, 7),
    (88, "Ra", "Radio", 226.0, "alcalino-terroso", 2, 7),
    (89, "Ac", "Attinio", 227.0, "attinide", 3, 10),
    (90, "Th", "Torio", 232.038, "attinide", 4, 10),
    (91, "Pa", "Protoattinio", 231.036, "attinide", 5, 10),
    (92, "U", "Uranio", 238.029, "attinide", 6, 10),
    (93, "Np", "Nettunio", 237.0, "attinide", 7, 10),
    (94, "Pu", "Plutonio", 244.0, "attinide", 8, 10),
    (95, "Am", "Americio", 243.0, "attinide", 9, 10),
    (96, "Cm", "Curio", 247.0, "attinide", 10, 10),
    (97, "Bk", "Berkelio", 247.0, "attinide", 11, 10),
    (98, "Cf", "Californio", 251.0, "attinide", 12, 10),
    (99, "Es", "Einsteinio", 252.0, "attinide", 13, 10),
    (100, "Fm", "Fermio", 257.0, "attinide", 14, 10),
    (101, "Md", "Mendelevio", 258.0, "attinide", 15, 10),
    (102, "No", "Nobelio", 259.0, "attinide", 16, 10),
    (103, "Lr", "Laurenzio", 266.0, "attinide", 17, 10),
    (104, "Rf", "Rutherfordio", 267.0, "transizione", 4, 7),
    (105, "Db", "Dubnio", 268.0, "transizione", 5, 7),
    (106, "Sg", "Seaborgio", 269.0, "transizione", 6, 7),
    (107, "Bh", "Bohrio", 270.0, "transizione", 7, 7),
    (108, "Hs", "Hassio", 269.0, "transizione", 8, 7),
    (109, "Mt", "Meitnerio", 278.0, "transizione", 9, 7),
    (110, "Ds", "Darmstadtio", 281.0, "transizione", 10, 7),
    (111, "Rg", "Roentgenio", 282.0, "transizione", 11, 7),
    (112, "Cn", "Copernicio", 285.0, "transizione", 12, 7),
    (113, "Nh", "Nihonio", 286.0, "metallo", 13, 7),
    (114, "Fl", "Flerovio", 289.0, "metallo", 14, 7),
    (115, "Mc", "Moscovio", 290.0, "metallo", 15, 7),
    (116, "Lv", "Livermorio", 293.0, "metallo", 16, 7),
    (117, "Ts", "Tennesso", 294.0, "alogeno", 17, 7),
    (118, "Og", "Oganesson", 294.0, "gas-nobile", 18, 7),
]

# Elettronegativita' di Pauling. None dove non e' definita/attendibile.
EN = {
    "H": 2.20, "He": None, "Li": 0.98, "Be": 1.57, "B": 2.04, "C": 2.55,
    "N": 3.04, "O": 3.44, "F": 3.98, "Ne": None, "Na": 0.93, "Mg": 1.31,
    "Al": 1.61, "Si": 1.90, "P": 2.19, "S": 2.58, "Cl": 3.16, "Ar": None,
    "K": 0.82, "Ca": 1.00, "Sc": 1.36, "Ti": 1.54, "V": 1.63, "Cr": 1.66,
    "Mn": 1.55, "Fe": 1.83, "Co": 1.88, "Ni": 1.91, "Cu": 1.90, "Zn": 1.65,
    "Ga": 1.81, "Ge": 2.01, "As": 2.18, "Se": 2.55, "Br": 2.96, "Kr": 3.00,
    "Rb": 0.82, "Sr": 0.95, "Y": 1.22, "Zr": 1.33, "Nb": 1.6, "Mo": 2.16,
    "Tc": 1.9, "Ru": 2.2, "Rh": 2.28, "Pd": 2.20, "Ag": 1.93, "Cd": 1.69,
    "In": 1.78, "Sn": 1.96, "Sb": 2.05, "Te": 2.1, "I": 2.66, "Xe": 2.60,
    "Cs": 0.79, "Ba": 0.89, "La": 1.10, "Ce": 1.12, "Pr": 1.13, "Nd": 1.14,
    "Pm": None, "Sm": 1.17, "Eu": None, "Gd": 1.20, "Tb": None, "Dy": 1.22,
    "Ho": 1.23, "Er": 1.24, "Tm": 1.25, "Yb": None, "Lu": 1.27, "Hf": 1.3,
    "Ta": 1.5, "W": 2.36, "Re": 1.9, "Os": 2.2, "Ir": 2.20, "Pt": 2.28,
    "Au": 2.54, "Hg": 2.00, "Tl": 1.62, "Pb": 2.33, "Bi": 2.02, "Po": 2.0,
    "At": 2.2, "Rn": None, "Fr": 0.7, "Ra": 0.9, "Ac": 1.1, "Th": 1.3,
    "Pa": 1.5, "U": 1.38, "Np": 1.36, "Pu": 1.28, "Am": 1.3, "Cm": 1.3,
    "Bk": 1.3, "Cf": 1.3, "Es": 1.3, "Fm": 1.3, "Md": 1.3, "No": 1.3,
    "Lr": None,
}

# Numeri di ossidazione piu' usati nel corso. Il primo e' quello principale.
OX = {
    "H": [1, -1], "Li": [1], "Be": [2], "B": [3], "C": [4, -4, 2],
    "N": [-3, 3, 5, 1, 2, 4], "O": [-2, -1], "F": [-1],
    "Na": [1], "Mg": [2], "Al": [3], "Si": [4, -4],
    "P": [5, 3, -3], "S": [-2, 4, 6], "Cl": [-1, 1, 3, 5, 7],
    "K": [1], "Ca": [2], "Sc": [3], "Ti": [4, 3], "V": [5, 4, 3, 2],
    "Cr": [3, 6, 2], "Mn": [2, 4, 7, 3, 6], "Fe": [2, 3], "Co": [2, 3],
    "Ni": [2, 3], "Cu": [2, 1], "Zn": [2], "Ga": [3], "Ge": [4, 2],
    "As": [3, 5, -3], "Se": [-2, 4, 6], "Br": [-1, 1, 3, 5, 7],
    "Rb": [1], "Sr": [2], "Y": [3], "Zr": [4], "Nb": [5], "Mo": [6, 4],
    "Tc": [7], "Ru": [3, 4], "Rh": [3], "Pd": [2, 4], "Ag": [1],
    "Cd": [2], "In": [3], "Sn": [2, 4], "Sb": [3, 5], "Te": [-2, 4, 6],
    "I": [-1, 1, 5, 7], "Cs": [1], "Ba": [2], "La": [3], "Ce": [3, 4],
    "Hf": [4], "Ta": [5], "W": [6], "Re": [7], "Os": [4], "Ir": [3, 4],
    "Pt": [2, 4], "Au": [3, 1], "Hg": [2, 1], "Tl": [1, 3], "Pb": [2, 4],
    "Bi": [3, 5], "Po": [4, 2], "At": [-1], "Fr": [1], "Ra": [2],
    "Ac": [3], "Th": [4], "Pa": [5], "U": [6, 4], "Np": [5], "Pu": [4],
}

# Ordine di riempimento di Aufbau (regola di Madelung).
AUFBAU = [
    ("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6), ("4s", 2),
    ("3d", 10), ("4p", 6), ("5s", 2), ("4d", 10), ("5p", 6), ("6s", 2),
    ("4f", 14), ("5d", 10), ("6p", 6), ("7s", 2), ("5f", 14), ("6d", 10),
    ("7p", 6),
]

GAS_NOBILI = [(2, "He"), (10, "Ne"), (18, "Ar"), (36, "Kr"), (54, "Xe"), (86, "Rn")]

# Configurazioni che non seguono l'Aufbau (scritte gia' in forma abbreviata).
ECCEZIONI = {
    24: "[Ar] 3d5 4s1", 29: "[Ar] 3d10 4s1", 41: "[Kr] 4d4 5s1",
    42: "[Kr] 4d5 5s1", 44: "[Kr] 4d7 5s1", 45: "[Kr] 4d8 5s1",
    46: "[Kr] 4d10", 47: "[Kr] 4d10 5s1", 57: "[Xe] 5d1 6s2",
    58: "[Xe] 4f1 5d1 6s2", 64: "[Xe] 4f7 5d1 6s2", 71: "[Xe] 4f14 5d1 6s2",
    78: "[Xe] 4f14 5d9 6s1", 79: "[Xe] 4f14 5d10 6s1", 89: "[Rn] 6d1 7s2",
    90: "[Rn] 6d2 7s2", 91: "[Rn] 5f2 6d1 7s2", 92: "[Rn] 5f3 6d1 7s2",
    93: "[Rn] 5f4 6d1 7s2", 96: "[Rn] 5f7 6d1 7s2", 103: "[Rn] 5f14 7s2 7p1",
}


def configurazione(z):
    """Configurazione elettronica abbreviata al gas nobile precedente."""
    if z in ECCEZIONI:
        return ECCEZIONI[z]

    rimasti, gusci = z, []
    for orb, cap in AUFBAU:
        if rimasti <= 0:
            break
        e = min(cap, rimasti)
        gusci.append((orb, e))
        rimasti -= e

    nobile, znobile = None, 0
    for zn, sym in GAS_NOBILI:
        if zn < z:
            nobile, znobile = sym, zn

    if nobile is None:
        return " ".join(f"{o}{e}" for o, e in gusci)

    # Tiene solo gli orbitali riempiti dopo il gas nobile.
    resto, saltati = [], 0
    for orb, e in gusci:
        if saltati < znobile:
            saltati += e
            continue
        resto.append(f"{orb}{e}")
    # Riordina per numero quantico principale, come si scrive nei testi.
    resto.sort(key=lambda s: (int(s[0]), "spdf".index(s[1])))
    return f"[{nobile}] " + " ".join(resto)


def blocco(colonna, riga):
    if riga in (9, 10):
        return "f"
    if colonna <= 2:
        return "s"
    if colonna >= 13:
        return "p"
    return "d"


def main():
    radice = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    elementi = []
    for n, sym, nome, massa, cat, x, y in BASE:
        # He e' nel blocco s anche se sta in colonna 18.
        b = "s" if sym == "He" else blocco(x, y)
        periodo = y if y <= 7 else (6 if y == 9 else 7)
        elementi.append({
            "n": n, "sim": sym, "nome": nome, "massa": massa,
            "cat": cat, "x": x, "y": y,
            "gruppo": x if y <= 7 else None,
            "periodo": periodo,
            "blocco": b,
            "config": configurazione(n),
            "en": EN.get(sym),
            "ox": OX.get(sym, []),
        })

    assert len(elementi) == 118, len(elementi)
    assert len({e["n"] for e in elementi}) == 118
    assert len({(e["x"], e["y"]) for e in elementi}) == 118, "posizioni doppie"

    percorso = os.path.join(radice, "dati", "elementi.json")
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(elementi, f, ensure_ascii=False, indent=0)
    print(f"scritti {len(elementi)} elementi in {percorso}")


if __name__ == "__main__":
    main()
