const API_URL = 'http://localhost:5000';
const REQUEST_TIMEOUT = 15000;

export const compareDna = async (seq1, seq2, runBlast) => {
    const controller = new AbortController();

    const timeoutId = setTimeout(() => {
        controller.abort();
    }, REQUEST_TIMEOUT);

    try {
        const response = await fetch(`${API_URL}/compare`, {
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
            let errorMessage = "Request failed";

            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorMessage;
            } catch {
                // non-JSON response
            }

            throw new Error(errorMessage);
        }

        return await response.json();

    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error(
                "Request timed out. The alignment or BLAST search may be taking too long."
            );
        }
        throw error;
    }
};