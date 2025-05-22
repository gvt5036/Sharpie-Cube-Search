// scripts/slim.js
const https = require('https');
const fs = require('fs');
const path = require('path');
const unzip = require('zlib').gunzipSync;

const url = 'https://mtgjson.com/api/v5/AllPrintings.json.gz';
const tempPath = path.join(__dirname, 'AllPrintings.json.gz');

function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, response => {
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', err => {
      fs.unlink(dest, () => reject(err));
    });
  });
}

(async () => {
  console.log('Downloading MTGJSON...');
  await downloadFile(url, tempPath);

  console.log('Unzipping...');
  const raw = fs.readFileSync(tempPath);
  const json = JSON.parse(unzip(raw).toString());

  const slim = [];

  for (const set of Object.values(json.data)) {
    for (const card of set.cards) {
      const originalText = card.originalText || "";
      const flavorText = card.flavorText || "";
      const combinedText = originalText + (flavorText ? `\n${flavorText}` : "");

      slim.push({
        uuid: card.uuid,
        name: card.name || card.faceName,
        setCode: set.code,
        number: card.number,
        originalType: card.originalType,
        originalText: originalText,
        flavorText: flavorText,
        combinedText: combinedText,
        scryfallId: card.identifiers?.scryfallId,
      });
    }
  }

  fs.writeFileSync('cards.json', JSON.stringify(slim, null, 2));
  console.log(`Wrote ${slim.length} cards to cards.json`);

  // Clean up
  fs.unlinkSync(tempPath);
  console.log('Cleaned up original downloaded file.');
})();
