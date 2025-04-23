const axios = require('axios');
const fs = require('fs');

async function downloadData() {
  try {
    // Update the URL to the correct Scryfall bulk data file
    const url = "https://data.scryfall.io/all-cards/all-cards-20250423092734.json";
    
    console.log("Requesting data from: ", url);

    // Make the API request to download the file
    const response = await axios.get(url, { responseType: 'stream' });

    // Save the data to a local file (e.g., 'all-cards.json')
    const writer = fs.createWriteStream('all-cards.json');
    response.data.pipe(writer);

    writer.on('finish', () => {
      console.log("Data downloaded and saved successfully.");
    });

    writer.on('error', (err) => {
      console.error("Error saving the file:", err);
    });
  } catch (err) {
    console.error("Error downloading data:", err);
  }
}

downloadData();
