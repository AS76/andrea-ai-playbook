# Estensione UK / Paesi Bassi
Motore: `/root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py`.
Invocare con il terminale del profilo Lex. Nessuna nuova API key o chiamata LLM nel motore.

## Comandi
- UK: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py uk --id ukpga/1996/18 --provision section/1 --as-of 2020-01-01 --archive`
- Olanda lavoro: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py nl --id BWBR0005290 --article 611 --as-of 2026-10-11 --archive`
- Olanda fisco: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py nl --id BWBR0011353 --article 2.1 --as-of 2026-10-11 --archive`
- Discovery NL: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py nl-search 'inkomstenbelasting' --as-of 2026-10-11 --limit 5`
- Guida: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py guidance --url https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/content/coming-to-work-in-the-netherlands-30-percent-facility --archive`
- Archivio NL: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py db-search werkgever --source wetten_nl --as-of 2026-10-11`
- Verificatore: `python3 /root/.hermes/profiles/lex/tools/lex-legal-research/lex_international.py verify --citation-file /percorso/citazione.json`

Sostituire la data d'esempio con quella dei fatti. Senza data dei fatti separare diritto attuale e applicazione storica.
La ricerca UK usa strumenti web realmente disponibili per scoprire l'identificativo; il motore recupera la disposizione identificata, non offre ancora una discovery UK automatica.

## Citazioni JSON
UK: `{"source":"legislation_uk","official_id":"ukpga/1996/18","provision":"section/1","as_of":"2020-01-01","quote":"Where an employee begins employment with an employer"}`.
NL: `{"source":"wetten_nl","official_id":"BWBR0005290","article":"611","as_of":"2026-10-11","quote":"De werkgever en de werknemer zijn verplicht zich als een goed werkgever"}`.
Guida: `{"source":"belastingdienst","url":"https://www.belastingdienst.nl/wps/wcm/connect/en/individuals/content/coming-to-work-in-the-netherlands-30-percent-facility","quote":"estratto letterale da verificare"}`.
Verifica positiva = identità, versione recuperata ed estratto letterale. NON prova applicabilità al caso o interpretazione.

## Regole UK
Distinguere England & Wales, Scotland, Northern Ireland. Non dedurre applicazione territoriale dal solo tipo di atto; leggere extent, commencement e disposizioni transitorie.
Mostrare `unapplied_effects` e lo stato `requires_legal_check`: modifiche non incorporate possono richiedere lettura degli atti modificativi. I metadati si riferiscono all'intero documento e possono comprendere effetti successivi alla data richiesta.
Conservare gli intervalli con fine ESCLUSIVA del dato UK. Una citazione storica non può usare un estratto della versione attuale.
Find Case Law NON integrato per analisi computazionale: verificare licenza per l'uso concreto prima di attivare. Non chiedere sottoscrizioni o aggirare limiti. Nessuna copertura esaustiva della giurisprudenza UK attestata.

## Regole Olanda e casi transfrontalieri
Diritto NL aggiunto all'ambito informativo del profilo; nessuna rappresentanza o parere vincolante.
BWB: intervallo dell'atto con fine inclusiva, controllo separato dell'entrata in vigore dell'articolo.
Citare testo originale olandese. Etichettare traduzioni come traduzioni di Lex; distinguere originali verificati e interpretazione.
Belastingdienst: guida amministrativa ufficiale, NON legge, sentenza o ruling personale. Verificare anno fiscale, disciplina transitoria e base normativa. Nessuna versione storica delle guide attestata.
Per trasferimenti IT/UK/NL ricostruire datore legale, firmatario, sede operativa, luogo abituale di lavoro, legge applicabile, foro, contratto e policy interne, tipo di mobilità e date.
Distinguere residenza civile/anagrafica e fiscale, ritenute, convenzioni contro doppia imposizione e previdenza. Non inferire diritto a trasferimento dalla gestione operativa del gruppo; richiedere evidenze per poteri e obblighi societari.
Verificare residenza e criteri fiscali; mai applicare automaticamente regimi expat, soglie o benefici. Niente moduli fiscali inviati o dati personali trasmessi alle fonti.
Cercare il miglior argomento contrario alla tesi di Andrea, senza assumere che policy interna e diritto di legge coincidano.

## Fonti e licenze controllate 2026-10-11
- https://legislation.github.io/data-documentation/api/overview.html
- https://legislation.github.io/data-documentation/reuse-licence.html : OGL v3.0, attribuzione Crown; eventuale contributo Westlaw da attribuire.
- https://www.overheid.nl/help/wet-en-regelgeving/een-eigen-kopie-van-het-basiswettenbestand-opbouwen : SRU e repository ufficiale; nessuna importazione massiva.
- https://data.overheid.nl/en/dataset/basis-wetten-bestand : CC0 1.0.
- https://www.belastingdienst.nl/wps/wcm/connect/bldcontenten/niet_in_enig_menu/individuals/copyright : CC0 salvo eccezioni dei componenti, niente endorsement implicito.
- https://caselaw.nationalarchives.gov.uk/permissions-and-licensing : licenza separata per computational analysis; connettore disabilitato.
- https://www.rechtspraak.nl/uitspraken/open-data : API pubblica, selezione e limiti. Connettore NON implementato in questa fase; non dichiarare precedenti NL verificati senza recuperarli con strumenti consentiti.

## Archivio e costi
Tabella additiva `lex_intl_records` nel solo DB `lex_legal`, FTS inglese/olandese e metadati completi JSON. Nessuna modifica a tabelle italiane/operative.
Snapshot locali selettivi; nessun cron o daemon. Richieste HTTPS con timeout, allowlist e limite 8 MiB; accessi serializzati, niente aggiramento TLS o anti-bot.
Il recupero e il verificatore non usano LLM. L'analisi di Lex usa il modello configurato e può generare costi; non promettere un servizio gratuito. Archivio usa il piano Neon esistente; incrementi di fatturazione non stimati.
