const API_URL = 'http://localhost:5000';
const REQUEST_TIMEOUT = 300000;

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

export const submitBlastJob = async (sequence) => {
    const response = await fetch(`${API_URL}/blast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence }),
    });

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "BLAST submission failed");
    }

    return response.json(); // returns { job_id: "..." }
};

export const pollBlastStatus = async (jobId) => {
    const response = await fetch(`${API_URL}/blast/status/${jobId}`);

    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Status check failed");
    }

    return response.json(); // returns { status: "pending"|"complete"|"failed", result?: {...} }
};