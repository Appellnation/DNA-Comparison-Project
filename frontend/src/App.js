import React, { useState } from 'react';
import { compareDna } from './services/api'; // Import your API service

function App() {
    const [seq1, setSequence1] = useState('');
    const [seq2, setSequence2] = useState('');
    const [similarity, setSimilarity] = useState(null);
    const [scoringMatrix, setScoringMatrix] = useState([]);

    const getCellStyle = (value) => {
        if (value > 0) return { backgroundColor:"#00fe08"}
        if (value < 0) return { backgroundColor: "#ff0019"}
        return {backgroundColor: "#399de4"}
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Pass seq1 and seq2 correctly to the API
            const result = await compareDna(seq1, seq2);
            setSimilarity(result.similarity_score);
            setScoringMatrix(result.scoring_matrix); // Adjust this if your backend returns a different structure
        } catch (error) {
            console.error("Error comparing DNA sequences:", error);
        }
    };

    return (
        <div>
            <h1>DNA Analysis</h1>

            <form onSubmit={handleSubmit}>
                <input 
                    type="text" 
                    value={seq1} 
                    onChange={(e) => setSequence1(e.target.value.toUpperCase())} 
                    placeholder="Enter first sequence" 
                />
                <input
                    type="text" 
                    value={seq2} 
                    onChange={(e) => setSequence2(e.target.value.toUpperCase())} 
                    placeholder="Enter second sequence" 
                />
                <button type="submit">Compare</button>
            </form>

            {similarity !== null && (
                <div>
                    <p>Similarity: {similarity}%</p>
                    {scoringMatrix.length > 0 && <MatrixDisplay matrix={scoringMatrix} seq1={seq1} seq2={seq2} />}
                </div>
            )}  
        </div>
    );
}

// Displaying the matrix
const MatrixDisplay = ({ matrix }) => {
    return (
        <div>
            <h3>Score Matrix</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th></th>
                        {/* Render column headers (first row of the matrix) */}
                        <th></th>
                        {seq2.split('').map((char, index) => (
                            <th key={index}>{char}</th>
                        ))}
                    </tr>
                </thead>

                <tbody>
                    {/* Render the rest of the matrix rows */}
                    {matrix.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                            {/* Labeling the Rows*/}
                            <th>
                                {rowIndex === 0 ? '-' : seq1[rowIndex - 1]}
                            </th>
                            {/* Matrix Cells*/}
                            {row.map((cell, colIndex) => (
                                <td 
                                    key={colIndex}
                                    style={getsCellStyle(cell)}
                                >
                                    {cell}
                                </td>     /* Render each cell */
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default App;
