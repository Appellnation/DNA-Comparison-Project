const API_URL = 'http://localhost:5000';

export const compareDna = async (seq1, seq2, runBlast) => {
    const controller = new AbortController();
    const timeout = 15000; // 15 seconds

    const timeoutId = setTimeout(() => {
        controller.abort();
    }, timeout);

    try {
        const response = await fetch("http://localhost:5000/compare", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                seq1,
                seq2,
                run_blast: runBlast
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Request failed");
        }

        return await response.json();

    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error("Request timed out. BLAST may be taking too long.");
        }
        throw error;
    }
};
