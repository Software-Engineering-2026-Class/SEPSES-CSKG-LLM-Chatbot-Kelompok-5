# SEPSES-CSKG-LLM-Chatbot-Kelompok-5
An LLM chat interface that integrates Cyber Security Knoledge Graph for cybersecurity risk analysis
---

## Deskripsi Proyek

Sistem chatbot berbasis LLM yang terintegrasi dengan **SEPSES Cybersecurity Knowledge Graph (CSKG)** untuk analisis keamanan siber. Mengimplementasikan arsitektur **Hybrid RAG + GraphRAG** yang menggabungkan:

- SPARQL query ke SEPSES KG (CVE, CWE, CAPEC, CPE, ATT&CK)
- Semantic search atas log keamanan lokal via ChromaDB
- Multi-LLM evaluation via OpenRouter (akses ke 100+ model dari berbagai provider)

## Anggota Kelompok:

| Nama | NIM | Github |
|-------|------|--------|
| Fahmi Abdillah Zain | 24/539422/PA/22904 | FahmiZain16 |
| Muhammad Dhafin A. G. | 24/539735/PA/22916 | Lemielll |
| Ajie Armansyah Sunaryo | 24/545286/PA/23170 | AjieArmansyahSunaryo |
| Satya Wira Pramudita | 24/543649/PA/23102 | satyawirapramudita |

## Tim Pengembang

| Peran               | Nama                             | Branch                 |
| ------------------- | -------------------------------- | ---------------------- |
| Knowledge Architect | Ajie Armansyah Sunaryo           | `feature/kg-engine`    |
| RAG Logic Dev       | Fahmi Abdillah Zain              | `feature/rag-logic`    |
| Full-Stack UI Dev   | Muhammad Dhafin Alfeizar Gandhan | `feature/frontend-ui`  |
| Evaluator & Log Dev | Satya Wira Pramudita             | `feature/eval-log-dev` |

---

## Arsitektur

```
User Query
    │
    ▼
Streamlit Frontend 
    │
    ▼
RAG Pipeline Orchestrator 
    ├── NL2SPARQL → SEPSES SPARQL Endpoint
    │       CVE / CWE / CAPEC / CPE / ATT&CK
    └── Vector Search → ChromaDB 
            Local Security Logs (Snort / Syslog / Windows Event)
    │
    ▼
LLM Generator (via OpenRouter API)
    OpenAI | Google | Anthropic | Meta | Mistral | 100+ models
    │
    ▼
Response + KG Graph Visualization + Source Citations
    │
    ▼
LLM-as-a-Judge Evaluator 
```

---

## Cara Menjalankan

### Prerequisites
- Python 3.10+
- OpenRouter API key: [https://openrouter.ai/keys](https://openrouter.ai/keys)
- (Opsional) Docker untuk Jena Fuseki lokal

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/satyawirapramudita/SEPSES-CSKG-LLM-Chatbot.git
cd SEPSES-CSKG-LLM-Chatbot

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
# Salin template dan isi nilai yang diperlukan
copy .env.example .env
# Edit .env dengan API key dan konfigurasi yang sesuai
```

### 3. Jalankan Aplikasi

```bash
streamlit run frontend/app.py
```

### 4. Jalankan Evaluasi

```bash
# Mock mode (tanpa API key)
python evaluation/run_eval.py --llm openai/gpt-4o-mini google/gemini-flash-latest --mock

# Real mode dengan berbagai model dari OpenRouter
python evaluation/run_eval.py --llm openai/gpt-4o-mini anthropic/claude-3.5-sonnet --category all
```

---

## 🐳 Quick Start with Docker

Cara tercepat untuk menjalankan seluruh stack (Fuseki SPARQL triplestore + Streamlit chatbot) tanpa setup manual Python environment.

### Prerequisites

| Komponen | Versi Minimum | Link Download |
|----------|--------------|---------------|
| **Docker Engine** | 20.10+ | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) |
| **Docker Compose** | v2.0+ (built-in di Docker Desktop) | Sudah termasuk di Docker Desktop |
| **OpenRouter API Key** | — | [openrouter.ai/keys](https://openrouter.ai/keys) |

> **Note:** Pada Windows dan macOS, cukup install [Docker Desktop](https://www.docker.com/products/docker-desktop/) yang sudah menyertakan Docker Engine dan Docker Compose.

### 1. Clone & Konfigurasi Environment

```bash
# Clone repository
git clone https://github.com/Software-Engineering-2026-Class/SEPSES-CSKG-LLM-Chatbot-Kelompok-5.git
cd SEPSES-CSKG-LLM-Chatbot-Kelompok-5

# Salin template environment variables
cp .env.example .env     # Linux/macOS
copy .env.example .env   # Windows (CMD)
```

Edit file `.env` dan isi minimal konfigurasi berikut:

```env
# [WAJIB] API key untuk akses LLM via OpenRouter
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key

# [OPSIONAL] Ganti model LLM sesuai kebutuhan (default: gpt-4o-mini)
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 2. Jalankan dengan Docker Compose

```bash
# Jalankan semua services (Fuseki + Chatbot)
docker compose up -d

# Atau jalankan hanya SPARQL triplestore (untuk development lokal)
docker compose up fuseki -d
```

### 3. Akses Aplikasi

| Service | URL | Deskripsi |
|---------|-----|-----------|
| **Streamlit Chatbot** | [http://localhost:8501](http://localhost:8501) | Antarmuka chatbot utama |
| **Fuseki Admin Panel** | [http://localhost:3030](http://localhost:3030) | SPARQL triplestore admin (user: `admin`, password: sesuai `FUSEKI_ADMIN_PASSWORD` di `.env`, default: `admin123`) |

### 4. Verifikasi Health Check

```bash
# Cek status semua container
docker compose ps

# Cek health Fuseki endpoint
curl http://localhost:3030/$/ping

# Cek log chatbot
docker compose logs chatbot --tail 50

# Cek log Fuseki
docker compose logs fuseki --tail 50
```

### Docker Service Architecture

```
┌─────────────────────────────────────────────────┐
│              Docker Compose Network             │
│                                                 │
│  ┌──────────────┐       ┌────────────────────┐  │
│  │   fuseki      │       │     chatbot        │  │
│  │  (Jena 4.9)   │◄──────│  (Python 3.10)     │  │
│  │  Port: 3030   │       │  Port: 8501        │  │
│  │               │       │                    │  │
│  │  SPARQL       │       │  Streamlit App     │  │
│  │  Triplestore  │       │  + RAG Pipeline    │  │
│  └──────────────┘       │  + ChromaDB        │  │
│        ▲                 └────────────────────┘  │
│        │                          │              │
│   fuseki_data                  ./data            │
│   (Docker Volume)          (Bind Mount)          │
└─────────────────────────────────────────────────┘
         │                          │
    ┌────┴────┐              ┌──────┴──────┐
    │ :3030   │              │   :8501     │
    │ Fuseki  │              │  Streamlit  │
    │  Admin  │              │  Chatbot UI │
    └─────────┘              └─────────────┘
         Host Machine (localhost)
```

### Perintah Docker Berguna

```bash
# Hentikan semua services
docker compose down

# Hentikan dan hapus volumes (reset data Fuseki)
docker compose down -v

# Rebuild image chatbot (setelah update kode/dependencies)
docker compose build chatbot

# Rebuild dan jalankan ulang
docker compose up -d --build

# Masuk ke shell container chatbot (debugging)
docker exec -it sepses_chatbot bash

# Lihat resource usage
docker stats sepses_chatbot sepses_fuseki
```

### Troubleshooting Docker

| Masalah | Solusi |
|---------|--------|
| Port `8501` sudah digunakan | Ubah port mapping di `docker-compose.yml`: `"8502:8501"` |
| Port `3030` sudah digunakan | Ubah port mapping di `docker-compose.yml`: `"3031:3030"` |
| Chatbot gagal start | Pastikan `.env` sudah terisi dengan benar, cek `docker compose logs chatbot` |
| Fuseki unhealthy | Cek memory: Fuseki butuh minimal ~2GB RAM (`JVM_ARGS=-Xmx2g`) |
| Build lambat | Build pertama kali akan mengunduh embedding model (~90MB). Build berikutnya akan lebih cepat berkat Docker cache |
| Permission denied (Linux) | Jalankan dengan `sudo` atau tambahkan user ke group docker: `sudo usermod -aG docker $USER` |

---

## 📁 Struktur Proyek

```
SEPSES-CSKG-LLM-Chatbot/
├── .env.example              # Template environment variables
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Fuseki + Ollama + App services
│
├── kg_engine/                # [Ajie] Knowledge Graph Engine
│   ├── sparql_client.py      # SEPSES SPARQL endpoint client
│   ├── graph_builder.py      # NetworkX graph builder
│   ├── ontology_schema.txt   # SEPSES ontology schema
│   └── queries/              # SPARQL query templates
│       ├── vulnerability_lookup.rq
│       ├── search_by_product.rq
│       └── get_capec_from_cve.rq
│
├── rag_logic/                # [Fahmi] RAG Pipeline
│   ├── rag_pipeline.py       # Main orchestrator
│   ├── nl2sparql.py          # NL → SPARQL (LangChain)
│   ├── multi_hop.py          # Multi-hop KG reasoning
│   ├── llm_connector.py      # GPT/Mistral abstraction
│   └── prompt_templates.py   # System/user prompts
│
├── log_analysis/             # [Satya] Log Analysis + Vector DB
│   ├── log_parser.py         # Snort/Syslog/WinEvent/Apache parser
│   ├── vector_store.py       # ChromaDB wrapper
│   └── hybrid_retriever.py   # BM25 + Semantic + RRF fusion
│
├── frontend/                 # [Dhafin] Streamlit Frontend
│   ├── app.py                # Multi-page Streamlit app
│   └── components/
│       ├── chat_window.py    # Chat UI + citations
│       ├── graph_visualizer.py # pyvis KG graph
│       ├── log_uploader.py   # Log file upload
│       └── eval_dashboard.py # Evaluation charts
│
├── evaluation/               # [Satya] Evaluation Framework
│   ├── benchmark_dataset.json # 30 pertanyaan benchmark
│   ├── grader.py             # LLM-as-a-Judge pipeline
│   ├── run_eval.py           # CLI runner
│   └── results/              # Output evaluasi
│
└── data/
    ├── cskg_dumps/           # SEPSES RDF dump files
    ├── chroma_db/            # ChromaDB persistent storage
    └── sample_logs/          # Sample security logs
        └── snort_sample.log

```

---

## Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| Security Analysis | Analisis CVE, CWE, CAPEC via SPARQL ke SEPSES KG |
| Threat Actor Analysis | Multi-hop traversal CVE→CWE→CAPEC→ATT&CK |
| Malware Investigation | Investigasi teknik malware via KG |
| Log Analysis | Upload + analisis Snort/Syslog/Windows Event Log |
| KG QA | Question-answering langsung atas SEPSES CSKG |
| Graph Visualization | Visualisasi interaktif relasi entitas KG |
| Multi-LLM Evaluation | Perbandingan berbagai model LLM via OpenRouter |

---

## Mengapa OpenRouter?

Proyek ini menggunakan **OpenRouter** sebagai unified API gateway untuk akses ke 100+ model LLM dari berbagai provider. Keuntungan:

| Keuntungan | Deskripsi |
|------------|-----------|
| **Single API** | Satu API key untuk akses semua model (OpenAI, Google, Anthropic, Meta, Mistral, dll.) |
| **Cost Efficiency** | Harga kompetitif dan transparan, bayar per token tanpa subscription |
| **Model Flexibility** | Mudah switch antar model tanpa mengubah kode - hanya ganti nama model |
| **No Infrastructure** | Tidak perlu maintain Ollama server atau GPU lokal |
| **Automatic Fallback** | Built-in failover ke model alternatif jika model utama down |
| **Rate Limiting** | Built-in rate limiting dan retry logic |

**Model yang tersedia:**
- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- **Google**: gemini-flash-latest, gemini-1.5-pro, gemini-1.5-flash
- **Anthropic**: claude-3.5-sonnet, claude-3-opus, claude-3-haiku
- **Meta**: llama-3-70b-instruct, llama-3-8b-instruct
- **Mistral**: mistral-7b-instruct, mixtral-8x7b-instruct, mixtral-8x22b-instruct
- Dan 100+ model lainnya: [https://openrouter.ai/models](https://openrouter.ai/models)

---


## Sumber Data SEPSES CSKG

| Dataset          | URL                                    |
| ---------------- | -------------------------------------- |
| SPARQL Endpoint  | https://w3id.org/sepses/sparql         |
| RDF Dumps        | https://w3id.org/sepses/dumps/         |
| CVE Vocabulary   | http://w3id.org/sepses/vocab/ref/cve   |
| CWE Vocabulary   | http://w3id.org/sepses/vocab/ref/cwe   |
| CAPEC Vocabulary | http://w3id.org/sepses/vocab/ref/capec |
| CPE Vocabulary   | http://w3id.org/sepses/vocab/ref/cpe   |
| CVSS Vocabulary  | http://w3id.org/sepses/vocab/ref/cvss  |

---
