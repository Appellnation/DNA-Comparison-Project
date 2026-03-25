import React, { useState, useEffect } from 'react';
import { compareDna, submitBlastJob, pollBlastStatus } from './services/apiService';


function App() {
    const [seq1, setSequence1] = useState('');
    const [seq2, setSequence2] = useState('');
    const [traceback, setTraceback] = useState([]);
    const [traceStep, setTraceStep] = useState(0);
    const [similarity, setSimilarity] = useState(null);
    const [error, setError] = useState(null);
    const [scoringMatrix, setScoringMatrix] = useState([]);
    const [alignedSeq1, setAlignedSeq1] = useState("");
    const [alignedSeq2, setAlignedSeq2] = useState("");
    const [runBlast, setRunBlast] = useState(false);
    const [blastResult, setBlastResult] = useState(null);
    const [blastLoading, setBlastLoading] = useState(false);
    const [loading, setLoading] = useState(false);
    const [animationSpeed] = useState(50);
   



    const getCellStyle = (value) => {
        const maxScore = 5; // Adjust in future mayhaps
        const intensity = Math.min(Math.abs(value) / maxScore, 1);

        if (value > 0) {
            return { backgroundColor: `rgba(0,255,0,${intensity})` };
        }
        if (value < 0) {
            return { backgroundColor: `rgba(255,0,0,${intensity})` };
        }
        return { backgroundColor: "#399de4" };
    };


   const handleSubmit = async (e) => {
        e.preventDefault();
        if (!seq1 || !seq2) { alert("Both sequences are required"); return; }

        setTraceStep(0);
        setBlastResult(null);
        setError(null);
        setLoading(true);

        try {
            // Step 1: Run alignment immediately
            const result = await compareDna(seq1, seq2);

            if (!Array.isArray(result.scoring_matrix)) {
                throw new Error("Invalid scoring matrix");
            }

            setSimilarity(result.similarity_score);
            setScoringMatrix(result.scoring_matrix);
            setTraceback(result.traceback);
            setAlignedSeq1(result.aligned_seq1);
            setAlignedSeq2(result.aligned_seq2);
            setLoading(false);  // matrix is ready, stop main loader

            // Step 2: Fire BLAST in background if requested
            if (runBlast) {
    setBlastLoading(true);
    const cleanSeq = result.aligned_seq1.replace(/-/g, "");

        try {
            const { job_id } = await submitBlastJob(cleanSeq);

            // Poll every 5 seconds until complete or failed
            const interval = setInterval(async () => {
                try {
                    const statusData = await pollBlastStatus(job_id);

                    if (statusData.status === "complete") {
                        setBlastResult(statusData.result);
                        setBlastLoading(false);
                        clearInterval(interval);
                    } else if (statusData.status === "failed") {
                        setBlastResult({ error: statusData.error });
                        setBlastLoading(false);
                        clearInterval(interval);
                    }
                    // If still "pending", do nothing — interval fires again in 5 seconds

                } catch (err) {
                    setBlastResult({ error: err.message });
                    setBlastLoading(false);
                    clearInterval(interval);
                }
            }, 5000);

        } catch (err) {
            setBlastResult({ error: err.message });
            setBlastLoading(false);
        }
    }

        } catch (err) {
            console.error(err);
            setError(err.message);
            setLoading(false);
        }
};

    useEffect(() => {
        fetch('https://dna-comparison-project.onrender.com').catch(() => {});
    }, []);

    useEffect(() => {
        if (traceback.length === 0) return;

        const interval = setInterval(() => {
            setTraceStep(prev =>
                prev < traceback.length ? prev + 1 : prev
            );
        }, animationSpeed);

        return () => clearInterval(interval);
    }, [traceback, animationSpeed]);

    return (
        <div>
            <h1>DNA Analysis</h1>

            {error && (
                <div style={{ color: "red", marginBottom: "10px" }}>
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "10px" }}>
                    <label style={{ fontSize: 13, color: "#aaa" }}>Sequence 1</label>
                    <input
                        type="text"
                        value={seq1}
                        onChange={(e) => setSequence1(e.target.value.toUpperCase())}
                        placeholder="Enter first nucleotide sequence (A, T, C, G, U)"
                        style={{
                            width: "100%",
                            padding: "10px 12px",
                            fontSize: 14,
                            fontFamily: "monospace",
                            backgroundColor: "#0d1825",
                            color: "#00e5a0",
                            border: "1px solid #1a3a4a",
                            borderRadius: 4,
                            boxSizing: "border-box"
                        }}
                    />
                    <label style={{ fontSize: 13, color: "#aaa" }}>Sequence 2</label>
                    <input
                        type="text"
                        value={seq2}
                        onChange={(e) => setSequence2(e.target.value.toUpperCase())}
                        placeholder="Enter second nucleotide sequence (A, T, C, G, U)"
                        style={{
                            width: "100%",
                            padding: "10px 12px",
                            fontSize: 14,
                            fontFamily: "monospace",
                            backgroundColor: "#0d1825",
                            color: "#00e5a0",
                            border: "1px solid #1a3a4a",
                            borderRadius: 4,
                            boxSizing: "border-box"
                        }}
                           />
                    </div>
                    <label style={{ display: "block", marginTop: "10px" }}>
                        <input
                            type="checkbox"
                            checked={runBlast}
                            onChange={(e) => setRunBlast(e.target.checked)}
                        />
                        Run BLAST taxonomic analysis
                    </label>
                    <button type="submit" disabled={loading}>
                        {loading ? "Comparing ..." : "Compare"}
                    </button>
                </form>
            {similarity !== null && (
                <>
                    <div>
                        <p>Similarity: {similarity}%</p>

                        <p><strong>Aligned Sequence 1:</strong> {alignedSeq1}</p>
                        <p><strong>Aligned Sequence 2:</strong> {alignedSeq2}</p>

                        <div style={{
                            marginTop: "20px",
                            padding: "10px",
                            backgroundColor: "#222",
                            color: "#00ff88",
                            fontFamily: "monospace"
                        }}>
                            <h3>Optimal Local Alignment</h3>
                            <div>{alignedSeq1}</div>
                            <div>{alignedSeq2}</div>
                        </div>

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

                    {runBlast && (
                        <div style={{
                            marginTop: "20px",
                            padding: "15px",
                            border: "1px solid #ccc",
                            borderRadius: "8px",
                            backgroundColor: "#f4f4f4"
                        }}>
                            <h3>BLAST Taxonomic Result</h3>

                            {blastLoading ? (
                                <p>Running BLAST analysis…</p>
                            ) : blastResult ? (
                                blastResult.title ? (
                                    <>
                                        <p><strong>Top Match:</strong> {blastResult.title}</p>
                                        <p><strong>Organism:</strong> {blastResult.taxonomy}</p>
                                    </>
                                ) : (
                                    <p>No significant BLAST match found.</p>
                                )
                            ) : (
                                <p>BLAST not run.</p>
                            )}
                        </div>
                    )}
              </>
            )}
        </div>
    );
}

// Displaying the matrix
const MatrixDisplay = ({ matrix, seq1, seq2, traceback, getCellStyle }) => {
    return(
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
