from enum import IntEnum
import numpy as np
import itertools
from Bio.Blast import NCBIWWW, NCBIXML

# Constants for the scores
class Score(IntEnum):
    MATCH = 1
    MISMATCH = -1
    GAP = -1

# Constants for the traceback directions
class Trace(IntEnum):
    STOP = 0
    LEFT = 1 
    UP = 2
    DIAGONAL = 3

# Function to read DNA sequences from user input
def get_user_input():
    seq1 = input("Enter the first DNA sequence (string of codons): ").strip()
    seq2 = input("Enter the second DNA sequence (string of codons): ").strip()
    return seq1, seq2

#Function to confirm sequences are DNA
def confirm_sequences_are_nucleotides(seq1, seq2):
    valid = {'A', 'T', 'G', 'C', 'U'}
    combined = itertools.chain(seq1, seq2)
    if not all (nucleotide in valid for nucleotide in combined):
        raise ValueError("Only valid nucleotide sequences are accepted.")
    

# Function to convert potential RNA sequences to DNA for uniform analyzing
def rna_to_dna(seq):
    return seq.replace("U","T")

#Function to ensure that the sequence is DNA (and convert RNA to DNA if needed)
def ensure_dna_sequence(sequence):
    return rna_to_dna(sequence.upper())



# Implementing Smith-Waterman algorithm for local sequence alignment
def smith_waterman(seq1, seq2):
    rows = len(seq1) + 1
    cols = len(seq2) + 1
    matrix = [[None for _ in range(cols)] for _ in range(rows)]

    max_score = 0
    max_pos = (0, 0)
    
    #Initialization step
    for i in range(rows):
        for j in range(cols):
            matrix[i][j] = {
                "score":0,
                "dirs":[],
                "match":False
            }

    # Fill in the matrix with scores and traceback directions
    for i in range(1, rows):
        for j in range(1, cols):
            is_match = seq1[i - 1] == seq2[j - 1]

            diag = matrix[i - 1][j - 1]["score"] + (
                Score.MATCH if is_match else Score.MISMATCH
            )
            up = matrix[i - 1][j]["score"] + Score.GAP
            left = matrix[i][j - 1]["score"] + Score.GAP

            score = max(0, diag, up, left)
            dirs = []
            
            if score == diag and score != 0:
                dirs.append("diag")
            if score == up and score != 0:
                dirs.append("up")
            if score == left and score != 0:
                dirs.append("left")
                
            matrix[i][j] = {
                "score": score,
                "dirs": dirs,
                "match": is_match if "diag" in dirs else False
                # match=True only when diagonal move AND characters equal
            }    

            if score > max_score:
                max_score = score
                max_pos = (i, j)

            #Traceback path storage    
    
    # Traceback to get the aligned sequences
    traceback_path = []
    aligned_seq1 = []
    aligned_seq2 = []

    i, j = max_pos
    while matrix[i][j]["score"] > 0:
        if i == 0 and j == 0:
            break
        traceback_path.append([i, j])

        if "diag" in matrix[i][j]["dirs"]:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif "up" in matrix[i][j]["dirs"]:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append("-")
            i -= 1
        elif "left" in matrix[i][j]["dirs"]:
            aligned_seq1.append("-")
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    return {
        "matrix": matrix,
        "traceback": traceback_path,
        "aligned_seq1": "".join(reversed(aligned_seq1)),
        "aligned_seq2": "".join(reversed(aligned_seq2)),
        "max_score": max_score
    }

#Function to make the alignment for the smith-waterman
def display_alignment_matrix(matrix, seq1, seq2, traceback_path=None):
    
    arrow_map = {"diag": "↖", "up": "↑", "left": "←"}

    # Print top header row (seq2 letters)
    print("     ", end="")
    for c in seq2:
        print(f"  {c}  ", end="")
    print()

    for i, row in enumerate(matrix):
        # Row header (seq1 letter or '-')
        row_char = '-' if i == 0 else seq1[i-1]
        print(f" {row_char} ", end="")

        for j, cell in enumerate(row):
            score = cell["score"]
            dirs = cell["dirs"]

            # Combine arrows
            arrow = "".join(arrow_map[d] for d in dirs) if dirs else " "
        
            # Determine color
            if traceback_path and [i, j] in traceback_path:
                color = "\033[93m"  # Yellow for traceback
            elif cell.get("match", False):
                color = "\033[92m"  # Green for match
            elif "diag" in dirs:
                color = "\033[91m"  # Red for mismatch
            elif "up" in dirs or "left" in dirs:
                color = "\033[94m"  # Blue for gaps
            else:
                color = "\033[0m"   # Default

            print(f"{color}{score:2}{arrow}\033[0m ", end="")

        print()  # new line for next row


# Function to calculate percentage similarity between two aligned sequences
def calculate_similarity(aligned_seq1, aligned_seq2):

    """
    Similarity = (matches / aligned length) * 100
    Gaps are treated as mismatches.
    """

    if len(aligned_seq1) != len(aligned_seq2):
        print("Error: Sequences must be of the same length to calculate similarity.")
        return None

    # Count the number of matches and mismatches (treat gaps as mismatches)
    matches = 0
    mismatches = 0
    total = 0
    
    for a, b in zip(aligned_seq1, aligned_seq2):
        # Count only non-gap positions
        if a != '-' and b != '-':
            total += 1
            if a == b:
                matches += 1
            else:
                mismatches += 1
        # If either sequence has a gap, count as mismatch
        elif a == '-' or b == '-':
            mismatches += 1
            total += 1
    
    # Calculate the percentage similarity, considering gaps as mismatches
    if total == 0:
        return 0.0  # Avoid division by zero if no characters align
    similarity = (matches / total) * 100
    return similarity

###Sending our sequence to BLAST 
###Parsing Taxanomy
def get_taxonomy_from_blast(query_sequence):
    #perform blast search - blastn is blast nucleotide sequences, nt is nucleotide database
    
    try:
        result_handle = NCBIWWW.qblast(
            program = "blastn",
            database ="nt",
            sequence = query_sequence,
            hitlist_size = 1
        )

        blast_record = NCBIXML.parse(result_handle)

        if not blast_record.alingments:
            return None, None
        
        top_alignment = blast_record.alignments[0]

        title = top_alignment.title

        #Extracting Organism Name from Reference Number(s)
        taxonomy = (
            title.split('[')[-1].replace(']', '')
        if '[' in title else "Unknown organism"
        )
        
        return title, taxonomy
    
    except Exception:
        return None, None

def get_top_blast_hits(query_sequence, max_hits = 3):
    """
    Run Blast on query sequence and return top 3 hits
    Each hit includes 'title', 'accession', 'e-value', and 'taxonomy'
    """
    try: 
        result_handle = NCBIWWW.qblast(
            program = 'blastn',
            database = 'nt',
            sequence = query_sequence,
            hitlist_size = max_hits
        )
        blast_records = NCBIXML.parse(result_handle)
        hits = []

        for blast_record in blast_records:
            for i, alignment in enumerate(blast_record.alignments):
                if i >= max_hits:
                    break
            
                for hsp in alignment.hsps:
                    title = alignment.title
                    accession = alignment.accession
                    e_value = hsp.expect

                    taxonomy = title.split('[')[-1].replace(']', '') if '[' in title else "Unknown organism"

                    hits.append({
                        "title": title,
                        "accession": accession,
                        "e_value": e_value,
                        "taxonomy": taxonomy
                    })
                    break
            break

        return hits

    except Exception as e:
        print(f"BLAST failed: {e}")
        return

if __name__ == "__main__":
    # Get user input for the two DNA sequences
    seq1, seq2 = get_user_input()
    seq1 = ensure_dna_sequence(seq1).upper()
    seq2 = ensure_dna_sequence(seq2).upper()
    
    if not seq1 or not seq2:
        print("Error: Both sequences must be provided.")
    else:
        # Executing the Smith-Waterman local alignment algorithm
        result = smith_waterman(seq1, seq2)
        output_1 = result["aligned_seq1"]
        output_2 = result["aligned_seq2"]

        # Displaying the aligned sequences
        print(f"Aligned Sequence 1: {output_1}")
        print(f"Aligned Sequence 2: {output_2}")
        
        # Calculate and display the percentage similarity
        similarity = calculate_similarity(output_1, output_2)
        if similarity is not None:
            print(f"Percentage Similarity: {similarity:.2f}%")

        