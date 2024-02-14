const { Builder, By, until } = require("selenium-webdriver");
const firefox = require("selenium-webdriver/firefox");

const fs = require("fs");
const { parse } = require("csv-parse");

var total_begin = Date.now(); //start logging time
var err_obj = new Object();
// Loads sites to crawl
const sites = [];
fs.createReadStream("./sites.csv")
  //fs.createReadStream("../test_crawl_lists/us-ca_test_list.csv")
  //fs.createReadStream("sites.csv")
  //fs.createReadStream("val_set_sites1.csv")
  .pipe(parse({ delimiter: ",", from_line: 2 }))
  .on("data", function (row) {
    sites.push(row[0]);
  })
  .on("error", function (error) {
    console.log(error.message);
  });

var options;
let driver;

// write a custom error
// we throw this the title of the site has a human check
// then we can identify sites that we can't crawl with the vpn on
class HumanCheckError extends Error {
  constructor(message) {
    super(message);
    this.name = "HumanCheckError";
  }
}

async function setup() {
  await new Promise((resolve) => setTimeout(resolve, 3000));
  options = new firefox.Options()
    .setBinary(firefox.Channel.NIGHTLY)
    .setBinary("C:/Program Files/Firefox Nightly/firefox.exe")
    //.setBinary("/Applications/Firefox Nightly.app/Contents/MacOS/firefox-bin")
    .setPreference("xpinstall.signatures.required", false)
    .setPreference("geo.enabled", true)
    .setPreference("geo.provider.use_corelocation", true)
    .setPreference("geo.prompt.testing", true)
    .setPreference(
      "geo.provider.network.url",
      "https://www.googleapis.com/geolocation/v1/geolocate?key=%GOOGLE_LOCATION_SERVICE_API_KEY%"
    )
    .setPreference("geo.prompt.testing.allow", true)
    .setPreference("browser.cache.disk.enable", false)
    .setPreference("browser.cache.memory.enable", false)
    .addExtensions("./spoof_geolocation.xpi")
    .addExtensions("./ext.xpi");

  options.addArguments("--headful");

  driver = new Builder()
    .forBrowser("firefox")
    .setFirefoxOptions(options)
    .build();
  // set timeout so that if a page doesn't load in 30 s, it times out
  await driver
    .manage()
    .setTimeouts({ implicit: 0, pageLoad: 30000, script: 30000 });
  console.log("built");

  const privacyPioneerWindow = await driver.getWindowHandle();
  await new Promise((resolve) => setTimeout(resolve, 2000));
  const windows = await driver.getAllWindowHandles();
  for (let w in windows) {
    if (windows[w] != privacyPioneerWindow) {
      // make a note of the original window
      const originalWindow = windows[w];
      // switch to privacy pioneer window
      //await driver.switchTo().window(privacyPioneerWindow);
      try {
        await driver.switchTo().alert().accept(); //close the alert
        // click skip tour button
        await driver
          .findElement(
            By.xpath("/html/body/div[3]/div/div/div/div[2]/div/button")
          )
          .click()
          .finally();
        await new Promise((resolve) => setTimeout(resolve, 2000));
        console.log("alert closed/tour skipped");
      } catch (e) {
        console.log("Error: " + e);
      } finally {
        await driver.close(); //close pp window
        await driver.switchTo().window(originalWindow);
        break;
      }
    }
  }

  //setting up the Spoof Geolocation extension
  // Miami: 25.761681, -80.191788
  // Los Angeles: 34.052235, -118.243683
  const TARGET_LAT = "41.562321"; // both need to have at least four digits after the decimal
  const TARGET_LONG = "-72.650650";
  const LOCATION = TARGET_LAT + ", " + TARGET_LONG;
  const spoofWindow = driver.getWindowHandle();
  try {
    await driver.get("https://webbrowsertools.com/geolocation/");
    console.log("loaded spoofing site");
    await new Promise((resolve) => setTimeout(resolve, 3000));
    await driver.switchTo().alert().sendKeys(LOCATION);
    await driver.switchTo().alert().accept();
    console.log("keys sent");
  } catch (e) {
    console.log(e.name);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    driver.switchTo().window(spoofWindow);
  }

  // await driver.manage().window().maximize();
  await new Promise((resolve) => setTimeout(resolve, 3000));
  console.log("setup complete");
}

async function visit_site(sites, site_id) {
  var error_value = "no_error";
  console.log(site_id, ": ", sites[site_id]);
  try {
    await driver.get(sites[site_id]);
    // console.log(Date.now()); to compare to site loading time in debug table
    await new Promise((resolve) => setTimeout(resolve, 30000));
    // check if access is denied
    // if so, throw an error so it gets tagged as a human check site
    var title = await driver.getTitle();
    if (
      (title.match(/Access/i) && title.match(/Denied/i)) ||
      title.match(/error/i) ||
      (title.match(/service/i) && title.match(/unavailable/i)) ||
      title.match(/Just a moment.../i) ||
      title.match(/you have been blocked/i) ||
      title.match(/site not available/i) ||
      title.match(/attention required/i) ||
      title.match(/access to this page has been blocked/i) ||
      (title.match(/site/i) && title.match(/temporarily unavailable/i)) ||
      (title.match(/site/i) && title.match(/temporarily down/i)) ||
      title.match(/403 forbidden/i) ||
      title.match(/pardon our interruption/i)
    ) {
      throw new HumanCheckError("Human Check");
    }
  } catch (e) {
    console.log(e);
    var msg = "";
    // we want to separate the reaching an error page from other webdriver errors
    if (e.message.match(/reached error page/i)) {
      msg = ": Reached Error Page";
    }
    // log the errors in an object so you don't have to sort through manually
    if (e.name + msg in err_obj) {
      err_obj[e.name + msg].push(sites[site_id]);
    } else {
      err_obj[e.name + msg] = [sites[site_id]];
    }
    console.log(err_obj);
    error_value = e.name; // update error value

    ///////////////
    // converting the JSON object to a string
    var err_data = JSON.stringify(err_obj);

    // writing the JSON string content to a file
    fs.writeFile("error-logging.json", err_data, (error) => {
      // throwing the error
      // in case of a writing problem
      if (error) {
        // logging the error
        console.error(error);

        throw error;
      }
      console.log("error-logging.json written correctly");
    });
    //////////////////////

    // if it's just a human check site, we don't need to restart
    if (e.name != "HumanCheckError") {
      if (e.message.match(/Failed to decode response from marionette/i)) {
        console.log(
          e.name + ": " + e.message + "-- driver should already have quit "
        );
      } else {
        driver.quit();
      }
      console.log("------restarting driver------");
      new Promise((resolve) => setTimeout(resolve, 10000));
      await setup(); //restart the selenium driver
    }
  }
  return error_value;
}

(async () => {
  await setup();
  var error_value = "no_error";
  for (let site_id_str in sites) {
    const site_id = Number(site_id_str);
    var begin_site = Date.now(); // for timing
    await new Promise((resolve) => setTimeout(resolve, 3500));

    error_value = await visit_site(sites, site_id);

    var end_site = Date.now();
    var timeSpent_site = (end_site - begin_site) / 1000;
    console.log(
      "time spent: ",
      timeSpent_site,
      "total elapsed: ",
      (end_site - total_begin) / 1000
    );
  }

  //@ts-ignore
  driver.quit();
})();
