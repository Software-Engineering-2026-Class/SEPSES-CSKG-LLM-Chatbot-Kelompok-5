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
python evaluation/run_eval.py --llm openai/gpt-4o-mini google/gemini-2.0-flash --mock

# Real mode dengan berbagai model dari OpenRouter
python evaluation/run_eval.py --llm openai/gpt-4o-mini anthropic/claude-3.5-sonnet --category all
```

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
│   ├── ontology_schema.ttl   # SEPSES ontology schema
│   └── queries/              # SPARQL query templates
│       ├── vulnerability_lookup.rq
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
- **Google**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
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

## 🔒 Security Notes

- Semua API key disimpan di `.env` (tidak di-commit ke Git)
- Lihat `.env.example` untuk template konfigurasi
- Input sanitization diimplementasikan di setiap endpoint
- Prepared statements digunakan untuk semua SPARQL queries

---
