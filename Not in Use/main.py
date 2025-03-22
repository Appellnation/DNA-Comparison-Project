import tkinter as tk 
from tkinter import messagebox
from backend.Smith_Waterman_Revised import smith_waterman, calculate_similarity

class DNASequenceAlignmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DNA Sequence Alignment Utilizing Smith-Waterman")

        #Adding Labels, Entery Fields, and Buttons
        self.create_widgets
    
    def create_widgets(self):
        #Label and entry for Seq1
        self.seq1_label = tk.Label(self.root, text = "Enter the first DNA sequence:")
        self.seq1_label.pack()

        self.seq1_entry = tk.Entry(self.roots, width = 50)
        self.seq1_entry.pack()

        #Label and entry for Seq2
        self.seq2_label = tk.Label(self.root, text="Enter the second DNA sequence:")
        self.seq2_label.pack()
        
        self.seq2_entry = tk.Entry(self.root, width=50)
        self.seq2_entry.pack()

        # Button to run the Smith-Waterman algorithm
        self.align_button = tk.Button(self.root, text="Run Smith-Waterman Alignment", command=self.run_alignment)
        self.align_button.pack()

        # Button to calculate similarity
        self.similarity_button = tk.Button(self.root, text="Calculate Similarity", command=self.calculate_similarity)
        self.similarity_button.pack()

        # Labels to display the results
        self.aligned_seq1_label = tk.Label(self.root, text="Aligned Sequence 1:")
        self.aligned_seq1_label.pack()

        self.aligned_seq1_result = tk.Label(self.root, text="")
        self.aligned_seq1_result.pack()

        self.aligned_seq2_label = tk.Label(self.root, text="Aligned Sequence 2:")
        self.aligned_seq2_label.pack()

        self.aligned_seq2_result = tk.Label(self.root, text="")
        self.aligned_seq2_result.pack()

        self.similarity_label = tk.Label(self.root, text="Similarity: Not Calculated")
        self.similarity_label.pack()

    def run_alignment(self):
        seq1 = self.seq1_entry.get().strip()
        seq2 = self.seq2_entry.get().strip()
        
        if not seq1 or not seq2:
            messagebox.showerror("Input Error", "Both sequences must be provided.")
            return

        aligned_seq1, aligned_seq2 = smith_waterman(seq1, seq2)
        
        # Update the UI with the aligned sequences
        self.aligned_seq1_result.config(text=aligned_seq1)
        self.aligned_seq2_result.config(text=aligned_seq2)

    def calculate_similarity(self):
        seq1 = self.seq1_entry.get().strip()
        seq2 = self.seq2_entry.get().strip()
        
        if not seq1 or not seq2:
            messagebox.showerror("Input Error", "Both sequences must be provided.")
            return

        aligned_seq1, aligned_seq2 = smith_waterman(seq1, seq2)
        similarity = calculate_similarity(aligned_seq1, aligned_seq2)
        
        # Update the UI with the similarity result
        self.similarity_label.config(text=f"Similarity: {similarity:.2f}%")

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = DNASequenceAlignmentApp(root)
    root.mainloop()