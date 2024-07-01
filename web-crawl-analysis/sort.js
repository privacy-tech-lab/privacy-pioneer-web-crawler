const fs = require('fs');

// Read the output JSON file
const outputFilePath = 'output.json';
const jsonData = fs.readFileSync(outputFilePath, 'utf8');
const tallyData = JSON.parse(jsonData);

// Sort the numbers within each property by their keys
for (const property in tallyData) {
    tallyData[property] = sortObjectByKeys(tallyData[property]);
}

// Function to sort an object by its keys
function sortObjectByKeys(obj) {
    const sorted = {};
    Object.keys(obj).sort((a, b) => Number(a) - Number(b)).forEach(key => {
        sorted[key] = obj[key];
    });
    return sorted;
}

// Write the sorted JSON data back to the output file
fs.writeFileSync(outputFilePath, JSON.stringify(tallyData, null, 2), 'utf8');
console.log('Sorted JSON data saved to output.json');
