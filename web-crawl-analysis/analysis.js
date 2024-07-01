const fs = require('fs');
const path = require('path');

// Specify the path to the folder containing JSON files
const folderPath = 'data';
const outputFilePath = 'output.json';

// Read the list of files in the folder
fs.readdir(folderPath, (err, files) => {
    if (err) {
        console.error('Error reading folder:', err);
        return;
    }

    // Object to store tallies and corresponding file names
    const tallyData = {};

    // Iterate through each file in the folder
    files.forEach(file => {
        if (path.extname(file).toLowerCase() === '.json') {
            const filePath = path.join(folderPath, file);
            const tally = processJsonFile(filePath);
            tallyData[file] = tally;
        }
    });

    // Write the tally data to the output JSON file
    fs.writeFileSync(outputFilePath, JSON.stringify(tallyData, null, 2), 'utf8');
    console.log('Output saved to output.json');
});

// Function to process a JSON file
function processJsonFile(filePath) {
    const jsonData = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(jsonData);

    console.log(`Processing file: ${filePath}`); // Display the file name

    // Object to store the name tally
    const tally = {
        typeTally: {},
        parentCompanyTally: {},
        rootUrlTally: {},
        permissionTally: {}
    }

// Iterate through each JSON object
data.forEach(jsonObject => {
    if (jsonObject.hasOwnProperty('typ')) {
        const type = jsonObject.typ;
        tally.typeTally[type] = (tally.typeTally[type] || 0) + 1;
    }

    if (jsonObject.hasOwnProperty('parentCompany')) {
        const parentCompany = jsonObject.parentCompany;
        tally.parentCompanyTally[parentCompany] = (tally.parentCompanyTally[parentCompany] || 0) + 1;
    }

    if (jsonObject.hasOwnProperty('rootUrl')) {
        const rootUrl = jsonObject.rootUrl;
        tally.rootUrlTally[rootUrl] = (tally.rootUrlTally[rootUrl] || 0) + 1;
    }

    if (jsonObject.hasOwnProperty('permission')) {
        const permission = jsonObject.permission;
        tally.permissionTally[permission] = (tally.permissionTally[permission] || 0) + 1;
    }
});
    return tally
// // Print the Button Name tally
// console.log('\nButton Name Tally:');
// for (const name in buttonNameTally) {
//     console.log(`${name}: ${buttonNameTally[name]} occurrences`);
// }

// // Print the View tally
// console.log('\nView Tally:');
// for (const view in viewTally) {
//     console.log(`${view}: ${viewTally[view]} occurrences`);
// }

// // Print the Third Party tally
// console.log('\nThird Party Tally:');
// for (const thirdParty in thirdPartyTally) {
//     console.log(`${thirdParty}: ${thirdPartyTally[thirdParty]} occurrences`);
// }

// // Print the Website tally
// console.log('\nWebsite Tally:');
// for (const website in websiteTally) {
//     console.log(`${website}: ${websiteTally[website]} occurrences`);
// }

// // Prepare the tally data in JSON format
// const outputData = {
//     fileName,
//     buttonNameTally,
//     viewTally,
//     thirdPartyTally,
//     websiteTally
// };

// // Write the tally data to a JSON file
// fs.writeFileSync('output.json', JSON.stringify(outputData, null, 2), 'utf8');

// console.log('Output saved to output.json');
}




