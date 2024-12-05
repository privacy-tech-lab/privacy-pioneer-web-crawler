/*

This file contains all of the hard-coded values that need to be used by the crawler.

*/

// Location values for each location that we will be crawling.
// More information regarding this issue can be found at https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler#81-gps-coordinates-and-zip-codes-when-using-vpns
// These values were obtained during validation by manually inspecting the data taken from various IP-based geolocation APIs.

const LOCATION_VALUES = {
  IOWA: {
    lat: 41.2591,
    long: -95.8517,
    zip: "51502",
  },
  OREGON: {
    lat: 45.6056,
    long: -121.1807,
    zip: "97058",
  },
  LA: {
    lat: 34.0544,
    long: -118.2441,
    zip: "90060",
    // zip: "90009",
  },
};

// Time constants
const ONE_MINUTE_IN_MS = 60000;
const FOREVER = 2147483647;

module.exports = {
  LOCATION_VALUES,
  ONE_MINUTE_IN_MS,
  FOREVER,
};
