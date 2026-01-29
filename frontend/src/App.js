import React, { useState, useEffect } from 'react';
import { compareDna } from './services/api';

function App() {
    const [seq1, setSequence1] = useState('');
    const [seq2, setSequence2] = useState('');
    const [traceback, setTraceback] = useState([]);
    const [traceStep, setTraceStep] = useState(0);
    const [similarity, setSimilarity] = useState(null);
    const [scoringMatrix, setScoringMatrix] = useState([]);
    const [runBlast, setRunBlast] = useState(false);
    const [blastResult, setBlastResult] = useState(null);
    const [blastLoading, setBlastLoading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [animationSpeed, setAnimationSpeed] = useState(300);



    const getCellStyle = (value) => {
        if (value > 0) return { backgroundColor:"#00fe08"}
        if (value < 0) return { backgroundColor: "#ff0019"}
        return {backgroundColor: "#399de4"}
    }


    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!seq1 || !seq2) {
        alert("Both sequences are required");
        return;
    }
        try {
            // Pass seq1 and seq2 correctly to the API
            setLoading(true);
            const result = await compareDna(seq1, seq2, runBlast);

            if (!Array.isArray(result.scoring_matrix)){
                throw new Error("There is an invalid scoring matrix");
            }

            setSimilarity(result.similarity_score);
            setScoringMatrix(result.scoring_matrix); // Adjust this if your backend returns a different structure
            setTraceback(result.traceback);
            setLoading(false);

        } catch (error) {
            console.error("Error comparing DNA sequences:", error);
        }finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (traceback.length === 0) return;

        const interval = setInterval(() => {
            setTraceStep(prev =>
                prev < traceback.length ? prev + 1 : prev
            );
        }, 300);

        return () => clearInterval(interval);
    }, [traceback]);

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
                <button type="submit" disabled={loading}>
                    {loading? "Comparing ..." : "Compare"}
                </button>
            </form>

            {similarity !== null && (
                <div>
                    <p>Similarity: {similarity}%</p>
                    {scoringMatrix.length > 0 && (
                        <MatrixDisplay
                            matrix={scoringMatrix}
                            seq1={seq1}
                            seq2={seq2}
                            traceback={traceback.slice(0, traceStep)}
                            getCellStyle={getCellStyle}
                        />
)}
                </div>
            )}  
        </div>
    );
}

// Displaying the matrix
const MatrixDisplay = ({ matrix, seq1, seq2, traceback, getCellStyle }) => {
    return (
        <div>
            <h3>Score Matrix</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th></th>
                        {/* Render column headers (first row of the matrix) */}
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

                            {row.map((cell, colIndex) => {
                                const isTraceback = traceback?.some(
                                    ([i, j]) => i === rowIndex && j === colIndex
                                );
                                const baseStyle = getCellStyle(cell.score);

                                return (
                                    <td
                                        key={colIndex}
                                        style={{
                                            ...baseStyle,
                                            backgroundColor: isTraceback
                                                ? "yellow"
                                                : baseStyle.backgroundColor
                                        }}
                                    >
                                        {cell.score}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default App;
