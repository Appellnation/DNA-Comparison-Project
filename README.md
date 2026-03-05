DNA Local Alignment Web Application

Overview
This full-stack web application performs local DNA sequence alignment using the Smith-Waterman algorithm and  provides users with the option for NCBI BLAST taxonomic analyses.

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
React -> Post
Flask Backend:
    - Validate sequences
    - Run Smith-Waterman
    - Optionally run BLAST
    - Return JSON response
React: 
    - Render alignment
    - Animation of traceback
    - Displays taxonomic result


Why This Project
My academic background is in biology, my senior thesis and research experience were heavily focused on viruses. This project bridges bioinformatics and software engineering by combining:
    - Algorithmic implementation
    - Backend API design
    - Frontend Visualization
    - External data integration
Essentially, it demonstrates the ability to build complete systems from algorithm(s) to UI.