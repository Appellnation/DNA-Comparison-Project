const API_URL = 'http://localhost:5000';

export async function compareDna(seq1, seq2, runBlast = false) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000); //20 seconds for timeout

    try {
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
            signal: controller.signal
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Server error');
        }

        return await response.json();

    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timed out. Please try again.');
        }
        throw error;

    } finally {
        // Always runs, even on error
        clearTimeout(timeoutId);
    }
}

