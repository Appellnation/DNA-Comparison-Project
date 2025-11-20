from flask import Flask, request, jsonify
import itertools
import numpy as np
from Bio.Blast import NCBIWWW, NCBIXML

from backend.Smith_Waterman_Revised import (
    get_user_input,
    confirm_sequences_are_nucleotides,
    rna_to_dna,
    ensure_dna_sequence, 
    smith_waterman, 
    calculate_similarity,
    get_taxonomy_from_blast
)

import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    seq1 = data.get('sequence1')
    seq2 = data.get('sequence2')

    #Confirm two sequences are given
    if not seq1 or not seq2:
        return jsonify({'error': 'Both sequences must be provided'}), 400
    
    #Confirm sequences are viable nucleotides only
    if not confirm_sequences_are_nucleotides([seq1, seq2]):
        return jsonify({'error': 'Please provide two valid nucleotide sequences - One or both sequences are not valid.'}), 400
    
    #Confirm sequences are all given, or have been converted to DNA
    if 'U' in seq1:
        seq1 = rna_to_dna(seq1)
    if 'U' in seq2:
        seq2 = rna_to_dna(seq2)

    try:
        #Call DNA analysis function
        aligned_seq1, aligned_seq2, similarity_score, scoring_matrix = smith_waterman(seq1, seq2)

        #Calculate the percentage similarity
        similarity = calculate_similarity(aligned_seq1, aligned_seq2)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'aligned_sequence_1': aligned_seq1,
        'aligned_sequence_2': aligned_seq2,
        'similarity_score': similarity_score,
        'similarity': similarity,
        'scoring_matrix': scoring_matrix.tolist()                #converting numpy array to list for JSON
    })

if __name__ == '__main__':
    app.run(debug = True)