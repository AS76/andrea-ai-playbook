# Update assistito OpenClaw — ripresa 2026-09-09

Esito: core aggiornato e operativo; accettazione complessiva PARTIAL. Decisione funzionale sull'orario e compatibilità context-vault restano aperte. Nessun nuovo consenso hook applicato.

## Evidenze verificate

- Release ufficiale https://github.com/openclaw/openclaw/releases/tag/v2026.9.3 indicata Latest durante questa verifica. CLI 2026.9.3 (1391f7c), gateway avviato con Node dedicato 24.21.0 e installazione /opt/openclaw-2026.9.3.
- RPC health autenticata nuovamente riuscita; 12 account Telegram running. Il campo lastError era vuoto nello snapshot ripreso, ma il conflitto intermittente getUpdates di findmy è nei log e anche in health-before.json: non è una regressione dimostrata dell'update e il singolo snapshot non ne prova la risoluzione.
- systemd active/running, PID 1980105, NRestarts=0; listener solo loopback IPv4/IPv6, Recv-Q=0.
- openclaw.json byte-identico a openclaw.json.before; routing e permessi quindi invariati. Guard attuale PASS_REVIEWED_UPSTREAM_SOURCE, cinque file verificati.
- Evidenze della sessione precedente rilette: 15 gruppi di test provider PASS; manifest alterato respinto; backup coerente 10.374.574.080 byte, 222775 membri e target richiesti presenti; quick_check dei quattro DB principali e dodici DB agente PASS; HTTP 10/10; Cleo via gateway ha restituito OPENCLAW_2026_9_3_AGENT_OK. Nessuna nuova consegna Telegram richiesta o eseguita: E2E Telegram non provato.
- Doctor/lint precedentemente eseguiti senza fix: warning per campo segreto in chiaro preesistente e due backup legacy Skill Workshop preservati. Non corretti implicitamente.
- Rollback solo runtime bloccato dopo migrazioni schema; vecchia installazione e backup preservati. Servono piano di compatibilità dati e protezione delle nuove scritture prima di un downgrade.

## Valutazione time-inject

Osservazione dell'utente confermata da docs/concepts/system-prompt.md, docs/concepts/timezone.md e moduli installati date-time/current-time/heartbeat-runner. Il core fornisce data locale e fuso nel Temporal Context, session_status per l'ora esatta e aggiornamento dell'orario heartbeat/cron. time-inject aggiunge la lettura automatica dettagliata dell'orologio e il fuso da stato viaggio.

Configurazione attuale: userTimezone assente, host Etc/UTC; plugin configurato Europe/Rome con useTravelTimezone=false. Il probe isolato carica il codice reale con filesystem simulato e dimostra che la lettura da ctx.pluginConfig ignora la configurazione disponibile su api.pluginConfig; il fallback abilita il viaggio. Non sono stati letti dati reali di viaggio nel test.

Raccomandazione: adottare il supporto nativo con agents.defaults.userTimezone=Europe/Rome e plugins.entries.time-inject.enabled=false. Patch proposta in proposed-native-time.json; dry-run delle due operazioni PASS in native-time-dry-run.log. Non applicata: cambia la funzione di iniezione automatica e attende la scelta dell'utente. Il fuso nativo si applica anche alle superfici documentate che usano userTimezone, incluse le ore attive heartbeat configurate con timezone user; non modifica le espressioni cron o i fusi espliciti dei singoli job.

## Context-vault: problema separato

Non è reso superfluo dalle funzioni temporali. Il suo before_prompt_build è bloccato dal nuovo gate allowConversationAccess. L'analisi dell'API installata e il probe isolato dimostrano inoltre che before_compaction legge event.context mentre l'API espone event.messages: un messaggio sintetico valido produce zero salvataggi. Anche ctx.pluginConfig non è il canale della configurazione dei typed hook. Il consenso da solo non ripara questi problemi. Il percorso di vault corrente è condiviso: l'isolamento per sessione/agente va verificato prima di una futura riattivazione del prompt hook.

Nessuna correzione o espansione di permessi context-vault applicata. La proposta precedente proposed-hook-permissions.json resta evidenza storica NON APPROVATA e non è più una proposta raccomandata da applicare in blocco.

## Prossimo passo

Scelta sull'adozione della patch nativa dell'orario, poi backup puntuale, applicazione, validazione e verifica del gateway. Context-vault richiede una correzione di compatibilità separata e verificata prima del consenso alle conversazioni. Ledger RUNNING, revisione non ancora richiesta, nessuna dichiarazione COMPLETE.
