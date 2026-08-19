#!/usr/bin/env python3
"""
Genera la banca domande a partire dalle dispense di Chimica.

    pip install pypdf
    export AI_API_KEY="la-tua-chiave"
    python3 tools/genera_domande.py ~/dispense --prova     # mostra cosa leggerebbe
    python3 tools/genera_domande.py ~/dispense             # genera davvero

Legge ogni PDF dalla cartella indicata, ne estrae il testo, chiede al modello un
insieme di domande a risposta multipla e scrive domande/<id>.json.
Aggiorna domande/index.json senza toccare l'ordine delle voci gia' sistemate.

Le dispense non entrano mai nel repository: lo script le legge da una cartella
locale e scrive solo i JSON.

Si puo' interrompere in qualsiasi momento: al rilancio salta i file gia' scritti.
"""

import argparse
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

MODELLI = {
    "gemini": "gemini-flash-latest",
    "anthropic": "claude-sonnet-5",
}

PAUSA = 2.0            # secondi tra una dispensa e l'altra
MAX_CARATTERI = 90000  # taglio di sicurezza sul testo di una dispensa
RESIDUO = "Da ordinare"

PROMPT = """Ricevi il testo di una dispensa universitaria di Chimica generale
(corso di laurea in Ingegneria gestionale, L-9).

Scrivi {n} domande a risposta multipla per prepararsi all'esame, che e' un quiz
a risposta multipla.

Regole ferree:
- Ogni domanda ha esattamente 4 opzioni e una sola risposta corretta.
- I distrattori devono essere gli errori che uno studente commette davvero:
  confusione tra grandezze simili, formula invertita, suffisso sbagliato,
  passaggio dimenticato. Mai opzioni assurde o palesemente fuori tema.
- Per OGNI opzione scrivi una riga che spiega perche' e' corretta o dove sta
  l'errore. Sono quattro spiegazioni per domanda, non una.
- Le spiegazioni delle opzioni sbagliate devono nominare l'errore, non limitarsi
  a dire che sono sbagliate.
- Copri gli argomenti della dispensa, non la chimica in generale.
- Se la dispensa contiene calcoli, almeno un terzo delle domande deve essere
  numerico, con i numeri che tornano davvero.
- Usa la notazione della dispensa. Scrivi le formule in testo semplice
  (H2SO4, Fe2O3): l'app trasforma i numeri in indici da sola.
- Niente lettere davanti alle opzioni: nessun "a)", nessun "1.".

Rispondi con SOLO un oggetto JSON valido, senza premesse e senza blocchi di
codice, in questa forma esatta:

{{
  "titolo": "<titolo breve dell'argomento, max 8 parole>",
  "gruppo": "<macro-area, es. \\"Struttura della materia\\", \\"Equilibri e soluzioni\\">",
  "domande": [
    {{
      "testo": "<la domanda>",
      "opzioni": ["<corretta>", "<errata>", "<errata>", "<errata>"],
      "giusta": 0,
      "perche": ["<perche' la prima e' corretta>", "<errore della seconda>",
                 "<errore della terza>", "<errore della quarta>"],
      "tag": "<una parola: atomo, legami, mole, stechiometria, soluzioni, equilibri, termodinamica, elettrochimica, organica>"
    }}
  ]
}}

Metti sempre la risposta corretta in prima posizione con "giusta": 0.
L'app rimescola le opzioni da sola a ogni somministrazione.
"""


# ----------------------------------------------------------------- lettura PDF

def estrai_testo(percorso):
    """Prova pypdf, poi pdftotext. Restituisce None se il PDF non ha testo."""
    testo = None
    try:
        from pypdf import PdfReader
        lettore = PdfReader(percorso)
        pezzi = []
        for pagina in lettore.pages:
            pezzi.append(pagina.extract_text() or "")
        testo = "\n".join(pezzi)
    except ImportError:
        pass
    except Exception as e:
        print(f"    pypdf non ce l'ha fatta ({e}), provo pdftotext")

    if not testo or len(testo.strip()) < 200:
        import shutil, subprocess
        if shutil.which("pdftotext"):
            try:
                testo = subprocess.run(
                    ["pdftotext", "-layout", percorso, "-"],
                    capture_output=True, text=True, timeout=120).stdout
            except Exception:
                pass

    if not testo or len(testo.strip()) < 200:
        return None

    testo = unicodedata.normalize("NFKC", testo)
    testo = re.sub(r"[ \t]+", " ", testo)
    testo = re.sub(r"\n{3,}", "\n\n", testo)
    return testo[:MAX_CARATTERI]


# ----------------------------------------------------------------- chiamate AI

def chiama_gemini(chiave, modello, testo, n):
    corpo = {
        "contents": [{"parts": [{"text": PROMPT.format(n=n) + "\n\n---\n\n" + testo}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 8192},
    }
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{modello}:generateContent")
    req = urllib.request.Request(
        url, data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": chiave})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    return "".join(p.get("text", "")
                   for p in d["candidates"][0]["content"]["parts"])


def chiama_anthropic(chiave, modello, testo, n):
    corpo = {
        "model": modello,
        "max_tokens": 8000,
        "temperature": 0.4,
        "messages": [{"role": "user",
                      "content": PROMPT.format(n=n) + "\n\n---\n\n" + testo}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "x-api-key": chiave,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.load(r)
    return "".join(b.get("text", "") for b in d["content"] if b.get("type") == "text")


def estrai_json(grezzo):
    """Il modello a volte incornicia il JSON: si tiene solo l'oggetto."""
    t = grezzo.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    i, j = t.find("{"), t.rfind("}")
    if i == -1 or j == -1:
        raise ValueError("nessun oggetto JSON nella risposta")
    return json.loads(t[i:j + 1])


# ----------------------------------------------------------------- validazione

def controlla(banca, id_arg):
    """Scarta le domande malformate invece di scrivere una banca rotta."""
    buone, scartate = [], 0
    for k, d in enumerate(banca.get("domande", []), start=1):
        if not isinstance(d, dict):
            scartate += 1
            continue
        opz = d.get("opzioni")
        perche = d.get("perche") or []
        if (not d.get("testo") or not isinstance(opz, list) or len(opz) != 4
                or not all(isinstance(o, str) and o.strip() for o in opz)
                or len(set(opz)) != 4
                or not isinstance(d.get("giusta"), int)
                or not 0 <= d["giusta"] <= 3):
            scartate += 1
            continue
        if len(perche) != 4:
            perche = (list(perche) + [""] * 4)[:4]
        buone.append({
            "id": f"{id_arg}-{len(buone) + 1}",
            "testo": d["testo"].strip(),
            "opzioni": [o.strip() for o in opz],
            "giusta": d["giusta"],
            "perche": [str(p).strip() for p in perche],
            "tag": str(d.get("tag", "")).strip() or "generale",
        })
    return buone, scartate


# ----------------------------------------------------------------- indice

def id_da_nome(nome, usati):
    n = 1
    while f"C{n:02d}" in usati:
        n += 1
    return f"C{n:02d}"


def carica_indice(cartella):
    p = os.path.join(cartella, "index.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {"titolo": "Chimica (L-9)", "gruppi": []}


def id_presenti(indice):
    return {a["id"] for g in indice["gruppi"] for a in g["argomenti"]}


def aggiungi_voce(indice, id_arg, titolo, gruppo):
    if id_arg in id_presenti(indice):
        return
    nome_gruppo = gruppo or RESIDUO
    esistente = next((g for g in indice["gruppi"] if g["gruppo"] == nome_gruppo), None)
    if esistente is None:
        esistente = {"gruppo": nome_gruppo, "argomenti": []}
        indice["gruppi"].append(esistente)
    num = str(len(esistente["argomenti"]) + 1)
    esistente["argomenti"].append({"id": id_arg, "num": num, "titolo": titolo})


# ----------------------------------------------------------------- programma

def main():
    ap = argparse.ArgumentParser(description="Genera la banca domande dalle dispense.")
    ap.add_argument("cartella", help="cartella con i PDF delle dispense")
    ap.add_argument("--provider", choices=["gemini", "anthropic"], default="gemini")
    ap.add_argument("--modello", default=None)
    ap.add_argument("--domande", type=int, default=15,
                    help="quante domande per dispensa (default 15)")
    ap.add_argument("--prova", action="store_true",
                    help="mostra cosa verrebbe letto, senza chiamare il modello")
    args = ap.parse_args()

    radice = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uscita = os.path.join(radice, "domande")
    os.makedirs(uscita, exist_ok=True)

    if not os.path.isdir(args.cartella):
        sys.exit(f"La cartella {args.cartella} non esiste.")

    pdf = sorted(f for f in os.listdir(args.cartella) if f.lower().endswith(".pdf"))
    if not pdf:
        sys.exit(f"Nessun PDF in {args.cartella}.")

    print(f"Trovate {len(pdf)} dispense in {args.cartella}\n")

    indice = carica_indice(uscita)
    usati = id_presenti(indice)
    # Gli id gia' presenti come file contano come occupati anche se non indicizzati.
    for f in os.listdir(uscita):
        m = re.match(r"^(C\d+)\.json$", f)
        if m:
            usati.add(m.group(1))

    # Mappa nome file -> id, cosi' rilanciando lo script non si riparte da capo.
    mappa_p = os.path.join(uscita, ".dispense.json")
    mappa = {}
    if os.path.exists(mappa_p):
        with open(mappa_p, encoding="utf-8") as f:
            mappa = json.load(f)

    chiave = os.environ.get("AI_API_KEY", "")
    if not args.prova and not chiave:
        sys.exit("Manca AI_API_KEY. Esporta la chiave e rilancia.")
    modello = args.modello or MODELLI[args.provider]

    for nome in pdf:
        percorso = os.path.join(args.cartella, nome)
        id_arg = mappa.get(nome)

        if id_arg and os.path.exists(os.path.join(uscita, f"{id_arg}.json")):
            print(f"[salto]  {nome} -> {id_arg}.json esiste gia'")
            continue

        print(f"[leggo]  {nome}")
        testo = estrai_testo(percorso)
        if not testo:
            print("         nessun testo estraibile: e' una scansione? Salto.\n")
            continue
        print(f"         {len(testo)} caratteri")

        if args.prova:
            print("         " + testo[:220].replace("\n", " ") + "…\n")
            continue

        if not id_arg:
            id_arg = id_da_nome(nome, usati)
            usati.add(id_arg)

        try:
            grezzo = (chiama_gemini(chiave, modello, testo, args.domande)
                      if args.provider == "gemini"
                      else chiama_anthropic(chiave, modello, testo, args.domande))
            banca = estrai_json(grezzo)
        except urllib.error.HTTPError as e:
            print(f"         il servizio ha risposto {e.code}: {e.read()[:200]}\n")
            continue
        except Exception as e:
            print(f"         non sono riuscito a leggere la risposta: {e}\n")
            continue

        domande, scartate = controlla(banca, id_arg)
        if not domande:
            print("         nessuna domanda valida, salto.\n")
            continue

        titolo = str(banca.get("titolo") or os.path.splitext(nome)[0])[:80]
        gruppo = str(banca.get("gruppo") or RESIDUO)[:60]

        with open(os.path.join(uscita, f"{id_arg}.json"), "w", encoding="utf-8") as f:
            json.dump({"id": id_arg, "titolo": titolo, "gruppo": gruppo,
                       "origine": nome, "domande": domande},
                      f, ensure_ascii=False, indent=1)

        aggiungi_voce(indice, id_arg, titolo, gruppo)
        mappa[nome] = id_arg
        with open(mappa_p, "w", encoding="utf-8") as f:
            json.dump(mappa, f, ensure_ascii=False, indent=1)
        with open(os.path.join(uscita, "index.json"), "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=1)

        print(f"         {id_arg}.json — {len(domande)} domande"
              + (f", {scartate} scartate" if scartate else "") + f" — «{titolo}»\n")
        time.sleep(PAUSA)

    print("Fatto. Rileggi qualche domanda prima di committare: il modello sbaglia,")
    print("e una domanda sbagliata ripassata venti volte è peggio di una in meno.")


if __name__ == "__main__":
    main()
