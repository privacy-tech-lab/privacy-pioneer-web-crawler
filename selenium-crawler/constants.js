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
  },
  AU: {
    lat: -33.8678,
    long: 151.2073,
    zip: "1001",
  },
  BR: {
    lat: -23.5475,
    long: -46.6361,
    zip: "01000",
  },
  ES: {
    lat: 40.4165,
    long: -3.7026,
    zip: "28004",
  },
  CA: {
    lat: 43.7064,
    long: -79.3986,
    zip: "M5A",
  },
  ZA: {
    lat: -26.2023,
    long: 28.0436,
    zip: "2041",
  },
  DE: {
    lat: 52.5244,
    long: 13.4105,
    zip: "10119",
  },
  IN: {
    lat: 28.6214,
    long: 77.2148,
    zip: "110001",
  },
  SG: {
    lat: 1.2897,
    long: 103.8501,
    zip: "018989",
  },
  KR: {
    lat: 37.566,
    long: 126.9784,
    zip: "03141",
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
