const API_URL = 'http://localhost:5000'; //Local API URL

export const compareDna = async (sequence1, sequence2) =>{
  try{
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sequence1,
        sequence2,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error comparing DNA sequences:', error);
    throw error; // Rethrow the error for further handling
  }
};

// Add more functions as needed for other API endpoints

