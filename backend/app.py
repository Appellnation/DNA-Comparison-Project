from flask import Flask, request, jsonify
from flask_cors import CORS
from Bio.Blast import NCBIWWW, NCBIXML
import logging

from Smith_Waterman_Revised import (
    confirm_sequences_are_nucleotides,
    rna_to_dna,
    smith_waterman,
    calculate_similarity,
)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

def get_taxonomy_from_blast(query_sequence):
    try:
        logging.info("Running BLAST query...")

        result_handle = NCBIWWW.qblast(
            program="blastn",
            database="nt",
            sequence=query_sequence,
            hitlist_size=1
        )

        blast_record = NCBIXML.read(result_handle)

        if not blast_record.alignments:
            logging.info("No BLAST alignments found.")
            return None

        top_alignment = blast_record.alignments[0]
        title = top_alignment.title
        logging.info(f"Raw BLAST title: {title}") 


        if '[' in title:
            taxonomy = title.split('[')[-1].replace(']', '')
        else:
            # Extract organism from title text after the last pipe character
            after_pipe = title.split('|')[-1].strip()
            # Take only the first 3 words (genus, species, strain identifier)
            taxonomy = ' '.join(after_pipe.split()[:3])

        logging.info(f"Top BLAST match: {taxonomy}")

        return {
            "title": title,
            "taxonomy": taxonomy
        }

    except Exception as e:
        logging.error(f"BLAST failed: {str(e)}")
        return None

@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    seq1 = data.get("seq1")
    seq2 = data.get("seq2")

    if not seq1 or not seq2:
        return jsonify({"error": "Both sequences must be provided"}), 400

    # Normalize input
    seq1 = seq1.strip().upper()
    seq2 = seq2.strip().upper()

    if not confirm_sequences_are_nucleotides(seq1, seq2):
        return jsonify({
            "error": "Please provide valid nucleotide sequences (A, T, C, G, U only)."
        }), 400

    # Convert RNA to DNA if needed
    if "U" in seq1:
        seq1 = rna_to_dna(seq1)

    if "U" in seq2:
        seq2 = rna_to_dna(seq2)

    try:
        logging.info("Running Smith-Waterman alignment...")
        result = smith_waterman(seq1, seq2)
        similarity = calculate_similarity(result["aligned_seq1"], result["aligned_seq2"])

    except Exception as e:
        logging.error(f"Alignment failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "similarity_score": similarity,
        "scoring_matrix": result["matrix"],
        "traceback": result["traceback"],
        "aligned_seq1": result["aligned_seq1"],
        "aligned_seq2": result["aligned_seq2"],
    })

@app.route('/blast', methods=['POST'])
def blast():
    data = request.get_json()
    sequence = data.get("sequence")

    if not sequence:
        return jsonify({"error": "No sequence provided"}), 400

    if len(sequence) < 20:
        return jsonify({"error": "Sequence too short for BLAST"}), 400

    result = get_taxonomy_from_blast(sequence)
    if not result:
        return jsonify({"error": "No BLAST match found"}), 404

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)