# SEPSES-CSKG-LLM-Chatbot-Kelompok-5
An LLM chat interface that integrates Cyber Security Knoledge Graph for cybersecurity risk analysis
---

## 📋 Deskripsi Proyek

Sistem chatbot berbasis LLM yang terintegrasi dengan **SEPSES Cybersecurity Knowledge Graph (CSKG)** untuk analisis keamanan siber. Mengimplementasikan arsitektur **Hybrid RAG + GraphRAG** yang menggabungkan:
- SPARQL query ke SEPSES KG (CVE, CWE, CAPEC, CPE, ATT&CK)
- Semantic search atas log keamanan lokal via ChromaDB
- Multi-LLM evaluation (GPT-4o-mini vs Mistral-7B)

Anggota Kelompok:

| Nama | NIM | Github |
|-------|------|--------|
| Fahmi Abdillah Zain | 24/539422/PA/22904 | FahmiZain16 |
| Muhammad Dhafin A. G. | 24/539735/PA/22916 | Lemielll |
| Ajie Armansyah Sunaryo | 24/545286/PA/23170 | AjieArmansyahSunaryo |
| Satya Wira Pramudita | 24/543649/PA/23102 | satyawirapramudita |

## 👥 Tim Pengembang

| Peran | Nama | Branch |
|-------|------|--------|
| Knowledge Architect | Ajie Armansyah Sunaryo | `feature/kg-engine` |
| RAG Logic Dev | Fahmi Abdillah Zain | `feature/rag-logic` |
| Full-Stack UI Dev | Muhammad Dhafin Alfeizar Gandhan | `feature/frontend-ui` |
| Evaluator & Log Dev | Satya Wira Pramudita | `feature/eval-log-dev` |

## 📚 Sumber Data SEPSES CSKG

| Dataset | URL |
|---------|-----|
| SPARQL Endpoint | https://w3id.org/sepses/sparql |
| RDF Dumps | https://w3id.org/sepses/dumps/ |
| CVE Vocabulary | http://w3id.org/sepses/vocab/ref/cve |
| CWE Vocabulary | http://w3id.org/sepses/vocab/ref/cwe |
| CAPEC Vocabulary | http://w3id.org/sepses/vocab/ref/capec |
| CPE Vocabulary | http://w3id.org/sepses/vocab/ref/cpe |
| CVSS Vocabulary | http://w3id.org/sepses/vocab/ref/cvss |

---
