import React, { useState } from 'react';
import { compareDna } from './services/api'; // Import your API service

function App() {
    const [array1, setArray1] = useState('');
    const [array2, setArray2] = useState('');
    const [similarity, setSimilarity] = useState(null);
    const [scoringMatrix, setScoringMatrix] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = await compareDna(array1.split(','), array2.split(','));
        setSimilarity(result.similarity);
        setScoringMatrix(result.scoring_matrix);
    };

    return (
        <div>
            <h1>DNA Analysis</h1>
            <form onSubmit={handleSubmit}>
                <input type="text" value={array1} onChange={(e) => setArray1(e.target.value)} placeholder="Enter first array" />
                <input type="text" value={array2} onChange={(e) => setArray2(e.target.value)} placeholder="Enter second array" />
                <button type="submit">Compare</button>
            </form>
            {similarity !== null && <p>Similarity: {similarity}%</p>}
        </div>
    );
}

const MatrixDisplay = ({ matrix }) => {
    return (
        <table>
            <thead>
                <tr>
                    {matrix[0].map((header, index) => (
                        <th key={index}>{header}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {matrix.slice(1).map((row, rowIndex) => (
                    <tr key={rowIndex}>
                        {row.map((cell, colIndex) => (
                            <td key={colIndex}>{cell}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

export default App;
