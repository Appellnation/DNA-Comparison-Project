from flask import Flask, request, jsonify
from flask_cors import CORS
from Bio.Blast import NCBIWWW, NCBIXML
import logging

from Smith_Waterman_Revised import (
    confirm_sequences_are_nucleotides,
    rna_to_dna,
    smith_waterman,
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

        taxonomy = (
            title.split('[')[-1].replace(']', '')
            if '[' in title else "Unknown Organism"
        )

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

    run_blast = data.get("run_blast", False)
    seq1 = data.get("seq1")
    seq2 = data.get("seq2")

    if not seq1 or not seq2:
        return jsonify({"error": "Both sequences must be provided"}), 400

    # Normalize input
    seq1 = seq1.strip().upper()
    seq2 = seq2.strip().upper()

    if not confirm_sequences_are_nucleotides([seq1, seq2]):
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

        blast_result = None

        if run_blast:
            query_sequence = result["aligned_seq1"].replace("-", "")

            if len(query_sequence) >= 20:
                blast_result = get_taxonomy_from_blast(query_sequence)
            else:
                logging.info("Sequence too short for BLAST.")
                blast_result = None

    except Exception as e:
        logging.error(f"Alignment failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "similarity_score": result["similarity"],
        "scoring_matrix": result["matrix"],
        "traceback": result["traceback"],
        "aligned_seq1": result["aligned_seq1"],
        "aligned_seq2": result["aligned_seq2"],
        "blast": blast_result
    })


if __name__ == "__main__":
    app.run(debug=True)