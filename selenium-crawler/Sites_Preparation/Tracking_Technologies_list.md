# Crawler Performance Test List Prepartion

Our 100-site crawler performance test list is consisted of 2 parts:

1. 50 random websites that includes 5 sites from each of the 8 countries' top 525 lists and 10 sites from US' top 525 list. The 8 countries are: (australia, brazil, canada, germany, india, singapore, south africa, spain)

2. 50 random websites that have high probability of using the following tracking technologies:
   - Monetization: Advertising, Analytics, Social Networking
   - Location: City, Fine Location, Corse Location, Region, ZIP Code
   - Tracking: Browser Fingerprint, Tracking Pixel, IP Address

From our experience the `Monetization` category and `Tracking Pixel` are the most common tracking technology used by websites. Therefore, we did not deliberately collect the websites that use those technologies. Instead, to make sure we have a good coverage of websites, our focuses are mainly on `location` (including IP Address, City, Fine Location, Corse Location, Region, and ZIP Code) and `Browser Fingerprinting`. In the end, the 50 websites by tracking technologies are consists of 30 websites that use location tracking technologies and 20 websites that use browser fingerprinting technologies.

## Location

To collect sites that may track the users' location, we have randomly selected 5 location collection wedgets from this list:

abtasty.com
intellimize.co
6sense.com
onetrust
dynamicyield.com
permutive.com
securiti.ai
ipinfo.io
termly.io
ip-api.com
ipdata.co
ipfind.com
ipapi.co

The selected wedgets are:

- [IPinfo](https://trends.builtwith.com/websitelist/IPinfo)
- [OneTrust](https://trends.builtwith.com/websitelist/OneTrust)
- [Termly](https://trends.builtwith.com/websitelist/Termly)
- [ipapi](https://trends.builtwith.com/websitelist/ipapi)
- [6sense](https://trends.builtwith.com/websitelist/6sense)

We then go to the [builtwith](https://builtwith.com/) and search for the websites that have been identified to use the above wedgets. (You can click on the above wedgets links to see the list of websites that use the above wedgets). We collect 50 websites for each wedgets (that is the amount builtwith provides for free). The list of websites is saved in the `Sites_Preparation/location_websites_list` folder.

## Brower Fingerprint

We have randomly selected 5 fingerprinting wedgets from the [Disconnect list](https://github.com/disconnectme/disconnect-tracking-protection/blob/master/services.json) and also our own [list](https://github.com/privacy-tech-lab/privacy-pioneer/blob/7e46e745ef226ec157c24a207937205b8f9963e2/src/assets/keywords.json#L50):

- [Leadinfo](https://trends.builtwith.com/websitelist/Leadinfo)
- [Fingerprint2](https://trends.builtwith.com/javascript/Fingerprint2)
- [TrenDemon](https://trends.builtwith.com/websitelist/TrenDemon)
- [Fingerprint.js](https://trends.builtwith.com/websitelist/Fingerprint.js)
- [MaxMind](https://trends.builtwith.com/websitelist/MaxMind)

We then go to the [builtwith](https://builtwith.com/) and search for the websites that have been identified to use the above wedgets. (You can click on the above wedgets links to see the list of websites that use the above wedgets). We collect 50 websites for each wedgets (that is the amount builtwith provides for free). The list of websites is saved in the `Sites_Preparation/fingerprint_websites_list` folder.
