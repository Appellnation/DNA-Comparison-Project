from flask import Flask, request, jsonify
from flask_cors import CORS
from Bio.Blast import NCBIWWW, NCBIXML

from .Smith_Waterman_Revised import (
    confirm_sequences_are_nucleotides,
    rna_to_dna,
    smith_waterman, 
    calculate_similarity,
    get_taxonomy_from_blast,
)

import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()

    if not data:
        return jsonify({'error' : "Invalid JSON payload"}), 400

    run_blast = data.get("run_blast", False)
    
    seq1 = data.get('seq1')
    seq2 = data.get('seq2')


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
        result = smith_waterman(seq1, seq2)
        similarity = calculate_similarity(
            result["aligned_seq1"],
            result["aligned_seq2="]
        )

        blast_result = None

        if run_blast:
            query_sequence = result["aligned_seq1"].replace("-", "")

            if len(query_sequence) >= 20:
                title, taxonomy = get_taxonomy_from_blast(query_sequence)
                blast_result = {
                    "title" : title,
                    "taxonomy" : taxonomy
                }
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'similarity_score': similarity,
        'scoring_matrix': result["matrix"],                #converting numpy array to list for JSON
        'traceback': result["traceback"],
        'blast': blast_result
    })

if __name__ == '__main__':
    app.run(debug = True)