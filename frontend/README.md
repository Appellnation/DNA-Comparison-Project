DNA Local Alignment Web APplication

Overview
This full-stack web application performs local DNA sequence alignment using the Smith-Waterman algorithm and optionally provides useres with NCBI BLAST taxonomic analyses.

This demonstrates:
    - Algorithm implementation (dynamic programming)
    - Bioinformatics integration (NCBI Blast)
    - REST API design (Flask)
    - A React frotend with animated matrix visualization
    - Full-stack async communication

Features:
    - Local sequence alignment (Smith-Waterman)
    - Interactive scoring matrix visualization
    - Animated traceback display
    - Alignment similarity percentage calculation
    - Optional BLAST integration for taxonomic identification
    - RNA -> DNA automatic conversion
    - Input validation and error handling

Tech Stack
Frontend:
    - React
    - JavaScript
    - Async Fetch API
    - Component-based architecture
Backend:
    - Flask
    - BioPython (NCBI BLAST)
    - Smith-Waterman custom implementation

Architecture
User Input -> React UI
