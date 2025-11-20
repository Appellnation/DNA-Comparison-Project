from enum import IntEnum
import numpy as np
import itertools
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

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
        print("Only valid nucleotide sequences are accepted.")
    return seq1, seq2
    

# Function to convert potential RNA sequences to DNA for uniform analyzing
def rna_to_dna(seq1, seq2):
    return seq1.replace("U", "T") and seq2.replace("U", "T")

#Function to ensure that the sequence is DNA (and convert RNA to DNA if needed)
def ensure_dna_sequence(sequence):
    if 'U' in sequence.upper():
        return rna_to_dna(sequence)
    return sequence



# Implementing Smith-Waterman algorithm for local sequence alignment
def smith_waterman(seq1, seq2):
    row = len(seq1) + 1
    col = len(seq2) + 1
    matrix = np.zeros((row, col), dtype=np.int32)
    tracing_matrix = np.zeros((row, col), dtype=np.int32)
    
    max_score = -1
    max_index = (-1, -1)
    
    # Fill in the matrix with scores and traceback directions
    for i in range(1, row):
        for j in range(1, col):
            match_value = Score.MATCH if seq1[i - 1] == seq2[j - 1] else Score.MISMATCH
            diagonal_score = matrix[i - 1, j - 1] + match_value
            vertical_score = matrix[i - 1, j] + Score.GAP
            horizontal_score = matrix[i, j - 1] + Score.GAP
            
            matrix[i, j] = max(0, diagonal_score, vertical_score, horizontal_score)
            
            if matrix[i, j] == 0:
                tracing_matrix[i, j] = Trace.STOP
            elif matrix[i, j] == horizontal_score:
                tracing_matrix[i, j] = Trace.LEFT
            elif matrix[i, j] == vertical_score:
                tracing_matrix[i, j] = Trace.UP
            elif matrix[i, j] == diagonal_score:
                tracing_matrix[i, j] = Trace.DIAGONAL
                
            if matrix[i, j] > max_score:
                max_index = (i, j)
                max_score = matrix[i, j]
    
    # Traceback to get the aligned sequences
    aligned_seq1 = ""
    aligned_seq2 = ""
    max_i, max_j = max_index
    
    while tracing_matrix[max_i, max_j] != Trace.STOP:
        if tracing_matrix[max_i, max_j] == Trace.DIAGONAL:
            aligned_seq1 += seq1[max_i - 1]
            aligned_seq2 += seq2[max_j - 1]
            max_i -= 1
            max_j -= 1
        elif tracing_matrix[max_i, max_j] == Trace.UP:
            aligned_seq1 += seq1[max_i - 1]
            aligned_seq2 += '-'
            max_i -= 1
        elif tracing_matrix[max_i, max_j] == Trace.LEFT:
            aligned_seq1 += '-'
            aligned_seq2 += seq2[max_j - 1]
            max_j -= 1
    
    return aligned_seq1[::-1], aligned_seq2[::-1], max_score, matrix

# I should probs implement a visualization of the matrix so the user can see whats going on

# Function to calculate percentage similarity between two aligned sequences
def calculate_similarity(aligned_seq1, aligned_seq2):
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
    result_handle = NCBIWWW.qblast("blastn", "nt", query_sequence)

    blast_records = NCBIXML.parse(result_handle)
    for blast_record in blast_records:
        for alignment in blast_record.alignments:
            #return the best match/top of the list
            for hsp in alignment.hsps:
                #hsp - high scoring pair - best local alignment
                print(f"subject: {alignment.title}")
                print(f"Taxonomy: {alignment.hit_id}") #hit_id - the info we're looking for
                return alignment.title, alignment.hit_id
    return None, None #Case where zero matches are found

if __name__ == "__main__":
    # Get user input for the two DNA sequences
    seq1, seq2 = get_user_input()
    
    if not seq1 or not seq2:
        print("Error: Both sequences must be provided.")
    else:
        # Encure both sequences are DNA (convert RNA to DNA if needed)
        seq1 = ensure_dna_sequence(seq1)
        seq2 = ensure_dna_sequence(seq2)
        # Executing the Smith-Waterman local alignment algorithm
        output_1, output_2 = smith_waterman(seq1, seq2)

        # Displaying the aligned sequences
        print(f"Aligned Sequence 1: {output_1}")
        print(f"Aligned Sequence 2: {output_2}")
        
        # Calculate and display the percentage similarity
        similarity = calculate_similarity(output_1, output_2)
        if similarity is not None:
            print(f"Percentage Similarity: {similarity:.2f}%")

        #Blast search
        match_title, taxanomy_info = get_taxonomy_from_blast(output_1)
        if match_title and taxanomy_info:
            print(f"Best match: {match_title}")
            print(f"Taxonomy: {taxanomy_info}")
        else:
            print("No taxonomic information has been found.")