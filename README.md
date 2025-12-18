# MyBank Online Banking

**Autore:**  
Manuel Faustini  
Matricola: 0312400584

Tema 1: La digitalizzazione dell'impresa  
Traccia 6: Sviluppo di una applicazione full-stack API-based per un'impresa del settore finanziario

**Tecnologie Utilizzate:**
*   **Frontend:** Vue.js 3
*   **Backend:** FastAPI
*   **Database:** SQLite

---

## Come Avviare l'Applicazione (con Docker Compose)

### Prerequisiti

È necessario avere installato **[Docker Desktop](www.docker.com)** (disponibile per macOS, Windows e Linux). Include tutti gli strumenti necessari (Docker Engine e Docker Compose).

### Passaggi per l'Avvio

1.  **Clonare il repository:**
    Apri il terminale ed esegui:
    ```bash
    git clone https://github.com/mfaust0/MyBank.git
    cd MyBank
    ```

2.  **Avviare i container:**
    Dalla directory principale del progetto, esegui il comando:
    ```bash
    docker-compose up --build
    ```

### Accesso all'Applicazione

Una volta che i log nel terminale mostrano "Application startup complete":

*   **Frontend (Applicazione Web):** Apri il browser e naviga su **[http://localhost:5173](http://localhost:5173)**.
*   **Backend (API Documentation - Swagger):** Puoi visualizzare e testare le API all'indirizzo **[http://localhost:8000/docs](http://localhost:8000/docs)**.

Il database SQLite verrà creato automaticamente nella cartella locale `./db_data/`.

---

## Struttura del Progetto

L'app è strutturata in due directory separate per il backend e il frontend:

*   `/frontend`: contiene la configurazione delle Routes, del servizio Axios e dello store Pinia, il codice delle Viste della SPA, la configurazione Nginx e Dockerfile per il client.
*   `/backend`: contiene il codice delle rotte, delle logiche di servizio, i moduli di utilità per la gestione del db e della sicurezza, i modelli SQLModel e gli schemi di validazione Pydantic, le dipendenze Python e Dockerfile per il server.
*   `docker-compose.yml`: per collegare frontend e backend

---