# 🧬 DNA Sequence Alignment & Taxonomy Pipeline

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-Frontend-61DAFB.svg)
![Flask](https://img.shields.io/badge/Flask-Backend-black.svg)
![BioPython](https://img.shields.io/badge/BioPython-BLAST-orange.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/Appellnation/DNA-Comparison-Project)

A full-stack bioinformatics web application that performs local DNA sequence alignment using the **Smith-Waterman algorithm** and optionally identifies organisms via **NCBI BLAST** taxonomic analysis.

> Built by a biology graduate combining domain expertise with full-stack software engineering — from algorithm implementation to interactive UI.


## 📸 Screenshots

### 1. Sequence Input Form

![Sequence Input Form](screenshots/DNA%20Analysis%20Home%20Screen.png)

This is the entry point of the application — users paste two nucleotide sequences (DNA or RNA) into the input fields and optionally enable BLAST taxonomic analysis before submitting.

---

### 2. Scoring Matrix with Traceback Animation

![Scoring Matrix](screenshots/Scoring%20Matrix.gif)

The Smith-Waterman scoring matrix is rendered cell by cell after alignment — the yellow traceback path animates automatically, visually tracing the optimal local alignment through the matrix.

---

### 3. Alignment Result & Similarity Score

![Alignment Result](screenshots/Result%20Alignment%20and%20Similarity%20Score.gif)

The optimal local alignment is displayed in a terminal-style output alongside a percentage similarity score, showing exactly where the two sequences match, mismatch, or contain gaps.

---

### 4. BLAST Taxonomic Result

![BLAST Result](screenshots/BLAST%20Result.gif)

When BLAST is enabled, the aligned sequence is asynchronously submitted to NCBI's nucleotide database and the taxonomic result fills in automatically in the background, displaying the organism name extracted from the top match — note that this may be a partial representation of the full organism classification.

---

## ✨ Features

- **Local Sequence Alignment** — Custom Smith-Waterman dynamic programming implementation
- **Interactive Scoring Matrix** — Color-coded visualization with animated traceback path
- **Similarity Scoring** — Percentage similarity calculated from aligned sequences
- **BLAST Taxonomic Analysis** — Optional NCBI BLAST integration to identify organism from sequence
- **RNA → DNA Conversion** — Automatic conversion of RNA input sequences
- **Input Validation** — Nucleotide-only enforcement (A, T, C, G, U)
- **Async Architecture** — Matrix renders immediately; BLAST runs in the background
- **Responsive Error Handling** — Descriptive errors for invalid input or failed requests

---

## 🧪 Sample Sequences for Testing

**Identical sequences (100% similarity):**
```
Sequence 1: ATCGTACGATCGTACG
Sequence 2: ATCGTACGATCGTACG
```

**Partial match (interesting alignment):**
```
Sequence 1: ATGGAGAGCCTTGTCCCTGGTTTCAACGAGAAAACACACGTCCACTCAAA
Sequence 2: AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATG
```

**BLAST test sequence (E. coli 16S rRNA — returns organism ID):**
```
AGAGTTTGATCCTGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATGCAAGTCGAACGGTAACAGGA
```

---

## 🏗️ Architecture

```
User Input (React UI)
        ↓
  POST /compare  →  Flask Backend
                        ├── Validate nucleotide sequences
                        ├── Convert RNA → DNA if needed
                        ├── Run Smith-Waterman alignment
                        └── Return matrix + aligned sequences
        ↓
  Matrix renders immediately in browser
        ↓
  POST /blast (async, background)  →  Flask Backend
                                           ├── Submit to NCBI BLAST
                                           └── Parse taxonomic result
        ↓
  BLAST result fills in when ready
```

---

## 🛠️ Tech Stack

**Frontend**
- React (functional components + hooks)
- JavaScript (async/await, Fetch API)
- Component-based architecture

**Backend**
- Python / Flask
- BioPython (NCBI BLAST integration)
- Flask-CORS

**Algorithm**
- Custom Smith-Waterman local alignment (dynamic programming)
- Scoring: Match +1, Mismatch -1, Gap -1

---

## 🚀 Running Locally

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip + npm
- An active internet conneciton (required for NCBI BLAST queries)

### Recommended — set up a Python virtual environment first
```bash
python -m venv env
env\Scripts\activate
```

### Python dependencies
```bash
pip install flask flask-cors biopython
```

### Node dependencies
```bash
npm install
```

### Optional but recommended
- A Python virtual environment to avoid package conflicts:
```bash
  python -m venv env
  source env/bin/activate       # Mac/Linux
  env\Scripts\activate          # Windows
  pip install flask flask-cors biopython
```
### Backend setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```
Flask runs at `http://localhost:5000`

### Frontend setup

```bash
cd frontend
npm install
npm start
```
React runs at `http://localhost:3000`

---

## 📁 Project Structure

```
DNA-Alignment-Pipeline/
├── backend/
│   ├── app.py                    # Flask API — /compare and /blast routes
│   └── Smith_Waterman_Revised.py # Smith-Waterman algorithm + utilities
├── src/
│   ├── App.js                    # Main React component
│   └── services/
│       └── apiService.js         # Fetch API calls with timeout handling
└── README.md
```

---

## 🔬 Algorithm Overview

The **Smith-Waterman algorithm** finds the optimal *local* alignment between two sequences — meaning it identifies the most similar region, even if the full sequences differ significantly. This makes it ideal for identifying conserved regions in DNA.

**How it works:**
1. Build a scoring matrix where each cell represents the best alignment score up to that position
2. Fill the matrix using: `score = max(0, diagonal + match/mismatch, up + gap, left + gap)`
3. Traceback from the highest-scoring cell to reconstruct the aligned sequences

This is the same family of algorithms used in tools like BLAST itself.

---

## 💡 Why I Built This

My academic background is in biology, with senior thesis and research experience heavily focused on viruses. This project bridges bioinformatics and software engineering by combining:

- **Algorithmic implementation** — dynamic programming from scratch
- **Backend API design** — RESTful Flask with proper error handling
- **Frontend visualization** — animated matrix with React state management
- **External data integration** — live NCBI BLAST queries

It demonstrates the ability to build complete systems — from algorithm to UI — grounded in real scientific context.