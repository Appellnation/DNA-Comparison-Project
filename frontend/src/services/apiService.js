const API_URL = 'http://localhost:5000'; //Local API URL

export async function compareDna(seq1, seq2, runBlast = false) {
    const response = await fetch('http://localhost:5000/compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            seq1,
            seq2,
            run_blast: runBlast
        }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Server error');
    }

    return response.json();
}

// Add more functions as needed for other API endpoints

