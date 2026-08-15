# Chimica — allenamento per l'esame

Strumento di studio per Chimica generale (L-9, Ingegneria gestionale), pensato per un
esame a **risposta multipla**. Non è un tutor che spiega: è un allenatore che ti fa
rispondere, tiene il conto di cosa ti resta e ti ripropone al momento giusto quello
che stai per dimenticare.

Un unico file `index.html`: nessun build, nessun backend. Si apre da GitHub Pages o da
qualsiasi server statico locale. L'allenamento, la tavola periodica e la nomenclatura
funzionano **offline e senza chiave API**.

## Le tre modalità

**Allenamento.** Il cuore. Sotto il pulsante di avvio, «Scegli gli argomenti» apre l'elenco
con le caselle: puoi restringere la sessione a uno o più argomenti — utile sotto esame, quando
servono solo i capitoli di una prova parziale. La scelta resta salvata. Per difetto sono attivi
tutti. Le domande vengono dalla banca in `domande/`, generata una
volta sola dalle tue dispense. Ogni risposta aggiorna una pianificazione a ripetizione
spaziata: se sbagli, la domanda torna domani; se la azzecchi più volte, si allontana
progressivamente. Le sessioni **mescolano argomenti diversi** invece di procedere a
blocchi — è più faticoso, ed è per questo che funziona: all'esame le domande non
arrivano ordinate per capitolo. Si risponde con i tasti 1–4 e si avanza con la barra
spaziatrice.

Dopo ogni risposta compare la spiegazione di **tutte e quattro** le opzioni, non solo
di quella giusta. In un quiz i tre distrattori non sono rumore: sono gli errori che il
docente si aspetta che tu faccia. Capirli è studiare quattro concetti al prezzo di uno.

**Tavola periodica.** Tutti e 118 gli elementi, con gruppo, periodo, blocco,
configurazione elettronica, elettronegatività e numeri di ossidazione. La *Sfida*
genera le domande dai dati stessi, quindi non finisce mai. Ogni elemento ha un livello
di padronanza da 0 a 3: con il colore impostato su «padronanza», la tavola si riempie
man mano che la impari. È la mappa dei progressi.

**Nomenclatura.** Un generatore deterministico, senza AI: costruisce composti dalle
regole e interroga in due direzioni, formula → nome e nome → formula. I distrattori non
sono casuali, sono gli errori tipici: il numero di ossidazione sbagliato (ferroso al
posto di ferrico), il suffisso scambiato (solfito al posto di solfato), gli indici
incrociati al contrario. A lato resta sempre visibile l'albero delle quattro domande:
la nomenclatura non è una lista da memorizzare, è una procedura da applicare.

## Come si studia con questa app

Il ciclo è questo, ed è diverso dal guardare i video a lezione:

1. Una dispensa alla volta, letta **una volta sola** per averne il senso generale.
2. Lo script ne estrae 15 domande e le mette in banca.
3. Da lì in poi quell'argomento vive dentro l'allenamento, non dentro il PDF.
4. Prima di aver studiato un argomento, il **pre-test** in Progressi ti fa 5 domande su
   cui sbaglierai quasi tutto. È voluto: rispondere a una domanda prima di conoscerne
   la risposta aumenta quanto ti resta di ciò che leggi dopo.
5. Tre sessioni da sette minuti in tre momenti morti valgono più di un'ora la domenica.
   Il contatore dei giorni consecutivi in alto serve solo a questo.

## Generare le domande dalle dispense

Le dispense non entrano mai nel repository: lo script le legge da una cartella locale e
scrive solo i JSON.

```bash
pip install pypdf
export AI_API_KEY="la-tua-chiave"

python3 tools/genera_domande.py ~/Downloads/Chimica --prova        # controlla cosa legge
python3 tools/genera_domande.py ~/Downloads/Chimica                # genera davvero
python3 tools/genera_domande.py ~/Downloads/Chimica --domande 20   # più domande per dispensa
```

Riconosce i PDF con testo estraibile. Si può interrompere in qualsiasi momento: al
rilancio salta le dispense già lavorate (tiene traccia in `domande/.dispense.json`).
Le domande malformate vengono scartate invece di finire in banca.

**Rileggi le domande prima di committare.** Il modello sbaglia, e una domanda sbagliata
ripassata venti volte fa più danno di una domanda in meno. Correggere un JSON è un
minuto di lavoro.

```bash
git add domande/ && git commit -m "domande dalle dispense" && git push
```

## Struttura della banca

`domande/index.json` è l'indice, curato a mano, e decide l'ordine degli argomenti.
Lo script aggiunge in coda al gruppo «Da ordinare» solo le voci nuove: sposta a mano
nel punto giusto del programma.

Ogni argomento è un file `domande/<id>.json`:

```json
{
 "id": "C04",
 "titolo": "Legame chimico",
 "gruppo": "2. Struttura della materia",
 "domande": [
  {
   "id": "C04-1",
   "testo": "...",
   "opzioni": ["corretta", "errata", "errata", "errata"],
   "giusta": 0,
   "perche": ["perché la prima è corretta", "errore della seconda", "...", "..."],
   "tag": "legami"
  }
 ]
}
```

La risposta corretta sta sempre in prima posizione: l'app rimescola le opzioni a ogni
somministrazione, quindi non c'è modo di imparare la posizione invece del contenuto.

## Tavola periodica

`dati/elementi.json` si rigenera con:

```bash
python3 tools/costruisci_elementi.py
```

Le configurazioni elettroniche sono calcolate con l'ordine di riempimento di Aufbau e
corrette a mano per le eccezioni note (cromo, rame, palladio, argento, platino, oro,
lantanidi e attinidi irregolari). L'elettronegatività è la scala di Pauling; dove non è
definita in modo attendibile il campo è vuoto invece che inventato.

## Chiave API

Serve **solo** al pulsante «Spiegami meglio» sotto una domanda: chiede al modello di
aggiungere qualcosa che le spiegazioni scritte non dicono già, opzionalmente con una
analogia da cucina o rugby. La chiave resta in `localStorage`, nel browser.

| Provider | Chiave | Note |
|---|---|---|
| Google Gemini | https://aistudio.google.com/apikey | ha un piano gratuito |
| Anthropic Claude | https://console.anthropic.com/settings/keys | a consumo |

## Aprire l'app in locale

`fetch` non funziona su `file://`, serve un server:

```bash
python3 -m http.server 8000
# poi apri http://localhost:8000
```

Su GitHub Pages funziona direttamente.

## Cosa viene salvato nel browser

`localStorage`, sotto le chiavi `chimica.*`: la pianificazione di ogni domanda, la
padronanza per elemento, i giorni consecutivi, le impostazioni. Nessun dato esce dal
dispositivo. Il pulsante «Azzera i progressi» in Progressi cancella tutto.
