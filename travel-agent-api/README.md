# Travel Agent API

Assistente di viaggio AI (FastAPI + LangChain + LangGraph) che cerca voli e hotel,
crea itinerari giorno per giorno e dà informazioni storiche sulle destinazioni.
È pensata per essere usata dal front-end Laravel fornito dal corso (`web_TravelAgent`), che non fa parte di questa consegna.

## Installazione

```bash
poetry install
cp .env.example .env
```

Inserire nel `.env` le proprie chiavi:

```
OPENAI_API_KEY=...
SERPAPI_API_KEY=...
OPENAI_MODEL=gpt-4o   # opzionale, default gpt-4o
```

Il file `.env` è escluso dal repository tramite `.gitignore`.

## Avvio

```bash
poetry run uvicorn travel_agent_api.main:app --reload --port 8080
```

- Stato del server: http://127.0.0.1:8080/
- Documentazione e test: http://127.0.0.1:8080/docs, endpoint `POST /chat/travel-agent`

## Struttura

```
travel_agent_api/
├── config.py                  
├── main.py                    
├── routes/chat_router.py      
├── services/agent_service.py
└── tools/
    ├── flights_finder.py          
    ├── hotels_finder.py           
    ├── chain_travel_plan.py       
    └── chain_historical_expert.py 
```

## Modifiche rispetto ai manuali

**Ambiente e struttura**
- Python richiesto `>=3.11`, necessario per pydantic e langchain-openai.
- La cartella `travel_agent_api/` è stata spostata fuori da `src/` e il `pyproject.toml` è stato aggiornato di conseguenza.
- Gli import `langchain.prompts` sono diventati `langchain_core.prompts`, perché LangChain 1.x ha rimosso il vecchio modulo.

**Configurazione**
- Creato `config.py`, che centralizza la lettura del `.env`. I tool importano le chiavi da qui invece di chiamare `os.getenv` in ogni file.
- Il modello OpenAI è configurabile con la variabile `OPENAI_MODEL` (default `gpt-4o`) invece di essere scritto nel codice.

**API**
- Aggiunto l'endpoint `GET /` di stato, che prima restituiva 404.
- Il router gestisce gli errori con `try/except` e `HTTPException` (500 con il messaggio d'errore), invece di lasciare crashare la richiesta.

**Tool**
- `chain_travel_plan`: `PydanticOutputParser` è stato sostituito con `model.with_structured_output(TravelPlanOutput)`. Prima il parser falliva perché al modello non venivano passate le istruzioni sul formato.
- `chain_historical_expert`: restituisce solo il testo (`result.content`) invece dell'intero oggetto messaggio.
- `flights_finder` e `hotels_finder` non restituiscono più il JSON completo di SerpApi, ma una versione ridotta con i campi utili:
  - voli: prezzo, durata, compagnia, orari, fino a 3+3 opzioni;
  - hotel: nome, prezzo, valutazione, servizi, link, fino a 5 risultati.

  Il JSON completo, ripetuto a ogni messaggio della conversazione, faceva superare il limite di contesto del modello (oltre 128k token), causando un errore 400 e il crash del front-end.
- `hotels_finder` gestisce il caso in cui SerpApi non restituisca `properties`. Prima andava in `KeyError`.
- Le ricerche SerpApi sono in italiano e in euro (`hl=it`, `gl=it`, `currency=EUR`).

**Tracing**

Ho aggiunto delle `print` con prefisso, per seguire il flusso nel terminale:

| Prefisso | Dove | Cosa mostra |
|---|---|---|
| `[CONFIG]` | `config.py` | modello in uso e presenza delle chiavi (True/False) |
| `[ROUTER]` | `chat_router.py` | numero di messaggi ricevuti, ultimo messaggio, eventuali errori |
| `[AGENT]` | `agent_service.py` | ogni messaggio della conversazione e i tool chiamati con i loro parametri |
| `[FLIGHTS]` / `[HOTELS]` | tool | numero di risultati trovati o errore SerpApi |

## Test eseguiti

| Test | Esito |
|---|---|
| Domanda storica (Rinascimento a Firenze) | chiama `chain_historical_expert` |
| Viaggio completo (Venezia, Roma) | chiama voli, hotel e itinerario con il numero di giorni corretto |
| Solo voli (MXP → BCN) | chiama `flights_finder` |
| Conversazione su più messaggi (Parigi, 3 messaggi) | l'agente ricorda destinazione, date e persone dai messaggi precedenti |

## Limitazioni note

- **Volo di ritorno**: per i voli andata e ritorno SerpApi restituisce solo l'andata. Il ritorno richiederebbe una seconda chiamata con `departure_token`, quindi gli orari del ritorno mostrati dall'agente non sono affidabili.
- Il parametro `stops: "1"` limita la ricerca ai voli diretti.
- L'itinerario di `chain_travel_plan` può essere generato in inglese, poi l'agente lo riassume in italiano.
- Ogni richiesta rimanda all'API l'intera cronologia della chat. Conversazioni molto lunghe aumentano tempi e costi: in quel caso conviene ricaricare la pagina.
