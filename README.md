<p align="center">
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/privacy-tech-lab/privacy-pioneer-web-crawler"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/releases"><img alt="GitHub Release Date" src="https://img.shields.io/github/release-date/privacy-tech-lab/privacy-pioneer-web-crawler"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/commits/main"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/privacy-tech-lab/privacy-pioneer-web-crawler"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/privacy-tech-lab/privacy-pioneer-web-crawler"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/issues?q=is%3Aissue+is%3Aclosed"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed-raw/privacy-tech-lab/privacy-pioneer-web-crawler"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/watchers"><img alt="GitHub watchers" src="https://img.shields.io/github/watchers/privacy-tech-lab/privacy-pioneer-web-crawler?style=social"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/privacy-tech-lab/privacy-pioneer-web-crawler?style=social"></a>
  <a href="https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/network/members"><img alt="GitHub forks" src="https://img.shields.io/github/forks/privacy-tech-lab/privacy-pioneer-web-crawler?style=social"></a>
  <a href="https://github.com/sponsors/privacy-tech-lab"><img alt="GitHub sponsors" src="https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86"></a>
</p>

<p align="center">
<img src="Privacy_Pioneer_Floating.svg" width="270" height="195">
</p>

# Privacy Pioneer Web Crawler

A web crawler for detecting websites' data collection and sharing practices at scale using [Privacy Pioneer](https://github.com/privacy-tech-lab/privacy-pioneer). This crawler utilizes Privacy Pioneer's code; however, this repository is not related to the actual development of the Privacy Pioneer extension. Instead, this repository is an implementation of Privacy Pioneer utilizing [Selenium](https://www.selenium.dev/) for browser automation. Thus, it is not necessesary to download/install the extension code on your own; the necessary components for the extension are already provided in this repository. The user only needs to clone the Privacy Pioneer repository if they would like to make their own [changes](#4-changing-the-extension-for-a-crawl) to the extension. In order for the extension to be used by Selenium, it needs to be [compiled and packaged](#4-changing-the-extension-for-a-crawl) in a xpi file. Since the crawler will only work with a compiled version of the extension, it is necessary for the two repositories to be separate.

The code in this repo is developed and maintained by the [Privacy Pioneer team](https://github.com/privacy-tech-lab/privacy-pioneer#privacy-pioneer).

## Notes on Setup

Our crawler is intended to be run in different geographic locations, with the goal of investigating different privacy laws and how websites adhere to them. To that end, you may use a VPN, Web Proxy, [cloud computing](https://cloud.google.com/), or some other method suited for your needs. We provide instructions for setting up on the cloud because of [problems](#5-known-issues) that we encountered with how we intended to use the crawler. We will also be outlining the steps to install the crawler locally, in case you want to use the crawler in some other fashion. If you are **not** planning to crawl on the cloud, then feel free to skip to the [crawler setup](#2-instructions-for-setting-up-the-crawler-on-windows).

## 1. Instructions for Creating a New VM on Google Cloud

This section will outline the necessary steps to create a VM on the cloud. You will need to create a project in the [Google console](https://console.cloud.google.com/). Unless otherwise specified, leave a setting at it's default value. **Click the triangles next to the step number to see an example of what you should see at each step.**

<details>
<summary>1. Navigate to the Compute Engine and click Create Instance.</summary>
<img src="documentation/step1.JPG" alt="step 1"/>
</details>
<details>
<summary>2. Choose the name, region, and zone for your machine. Your decision should reflect what location you'd like to crawl from.</summary>
<img src="documentation/step2.JPG" alt="step 2"/>
</details>
<details>
<summary>3. Select the appropriate type of machine you'd like to use. If you're on the fence about whether or not your machine will be powerful enough, it's better to overestimate. We've had <a href="#5-known-issues">issues</a> with weaker machines where <a href="https://www.selenium.dev/">Selenium</a> stops working when a machine doesn't have sufficient memory.</summary>
<img src="documentation/step3.JPG" alt="step 3"/>
</details>
<details>
<summary>4. Change the server boot disk to Windows. In theory, there's no reason why you couldn't run this crawler on a Linux server. However, we haven't tested this, and we recommend the Windows route because you have easy access to a GUI. This makes checking if the crawler is operating as expected significantly easier.</summary>
<img src="documentation/step4.JPG" alt="step 4"/>
<img src="documentation/step4-5.JPG" alt="step 4.5">
</details>
<details>
<summary>5. Allow HTTP and HTTPS messages through the firewall. Then, click "Create".</summary>
<img src="documentation/step5.JPG" alt="step 5"/>
</details>
<details>
<summary>6. Now that you have your server, click on the triangle next to "RDP" and select "Set Windows Password". Be sure to save these credentials somewhere safe, as <strong>they will not be shown again</strong>.</summary>
<img src="documentation/step6.JPG" alt="step 6"/>
</details>

You should now have a working Google Cloud VM. To connect to the VM, use the Remote Desktop Connection app on Windows. Provide the external IP, username, and password. After connecting, you should see the server desktop. Next, you'll need to go through the crawler setup instructions.

**Note:** When crawling with multiple locations, you can avoid the hassle of setting up for each VM by using a [machine image](https://cloud.google.com/compute/docs/machine-images).

## 2. Instructions for Setting up the Crawler on Windows

The previous steps were getting you ready to set the crawler up on the cloud. Now, we'll actually be setting up the crawler. This process is identical locally and on the cloud.

**Note:** The crawler requires that [Firefox Nightly](https://www.mozilla.org/en-US/firefox/channel/desktop/) be installed

Start by cloning this repo. If you want to make changes to the Privacy Pioneer extension for the crawl, then look [here](#4-changing-the-extension-for-a-crawl) for a guide. If you want to use the extension as we intend to use it, then you can ignore said guide.

[Install MySQL and the MySQL shell](https://dev.mysql.com/doc/mysql-shell/8.0/en/mysql-shell-install.html). Once installed, enter the MySQL Shell and run the following commands:

```bash
\connect root@localhost
```

Enter your MySQL root password. If you haven't set this up yet, then the shell should prompt you to create one. Use password `abc`

Next, switch the shell over from JS to SQL mode.

```bash
\sql
```

To set the crawler up for accessing the database via your root account run:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'abc';
```

```sql
FLUSH PRIVILEGES;
```

### 2.1 Database Setup

Next, we will set up the MySQL database. This is important because we need a place to store the [evidence](https://github.com/privacy-tech-lab/privacy-pioneer?tab=readme-ov-file#7-privacy-practice-analysis) that Privacy Pioneer will find. Interactions with the database will be managed by the scripts located in the [rest-api](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/tree/main/rest-api) directory. We are also using a special [version](https://github.com/privacy-tech-lab/privacy-pioneer/tree/ppcrawl) of Privacy Pioneer that is designed to interact with this database.

First, in the MySQL shell, create the database:

```sql
CREATE DATABASE analysis;
```

Then, access it:

```sql
USE analysis;
```

Lastly, create a table where any evidence that Privacy Pioneer finds will be stored:

```sql
CREATE TABLE entries
  (id INTEGER PRIMARY KEY AUTO_INCREMENT, timestp varchar(255), permission varchar(255), rootUrl varchar(255),
  snippet varchar(4000), requestUrl varchar(4000), typ varchar(255), ind varchar(255), firstPartyRoot varchar(255),
  parentCompany varchar(255), watchlistHash varchar(255),
  extraDetail varchar(255), cookie varchar(255), loc varchar(255));
```

You can now exit the MySQL shell.

In the [rest-api](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/tree/main/rest-api) folder, create a new file called `.env`, and save the following to that file:

```bash
DB_CONNECTION=mysql
DB_HOST=localhost
DB_DATABASE=analysis
DB_USERNAME=root
DB_PASSWORD=abc
```

### 2.2 Crawler Setup

Lastly, you will need to manually set the zip code and the GPS coordinates that you will be crawling from.
You can accomplish this by opening up the [local crawler](https://github.com/privacy-tech-lab/privacy-pioneer-web-crawler/blob/main/selenium-crawler/local-crawler.js) script `local-crawler.js` and modifying the following values:

```js
const TARGET_LAT = 10.12; // replace this value with your intended latitude
const TARGET_LONG = -11.12; // replace this value with your intended longitude
const TARGET_ZIP = "011000"; // replace this value with your intended zip code (note that it must be a string)
```

## 3. Instructions for Running the Crawler

Using the terminal, enter the `privacy-pioneer-web-crawler/rest-api` directory. Run either:

```bash
npm install
node index.js
```

or

```bash
npm install
npm start
```

In another instance of the terminal, enter the `privacy-pioneer-web-crawler/selenium-crawler` directory, and run either:

```bash
npm install
node local-crawler.js
```

or

```bash
npm install
npm start
```

These two commands are enough to get the crawl to run. You will know the crawl is working when an instance of Firefox Nightly opens up and it looks like this:

<img src="./documentation/working-crawl.JPG" />

## 4. Changing the Extension for a Crawl

In case you should need it, here are the steps that you will need to follow in order to have your changes to [Privacy Pioneer](https://github.com/privacy-tech-lab/privacy-pioneer) reflected in your crawl.

1. Clone the Privacy Pioneer repo and make any changes that you'd like to see.

   **Note**: If you are making your own version of the crawler, then you will need to remember to enable "crawl mode" within the extension source code. The instructions for doing that can be found in the comments located [here](https://github.com/privacy-tech-lab/privacy-pioneer/blob/main/src/background/background.js). The gist is that you will need to set the flag `IS_CRAWLING` to `true`. If you are testing changes to the crawler, you will also need to set the `IS_CRAWLING_TESTING` flag to true. This is necessary so that functionality related to setting the location data and recording crawl data are enabled.

2. Once the changes have been made, run `npm run build` from within the `privacy-pioneer` directory.
3. Navigate to the newly made `dev` directory.
4. In the `manifest.json` file, add the following code at the bottom (within the json). Firefox will not let you add an extension without this ID.

   ```json
   "browser_specific_settings": {
       "gecko": {
         "id": "{daf44bf7-a45e-4450-979c-91cf07434c3d}"
       }
     }
   ```

5. Within the `dev` directory, send all the files to a zip file.
6. Rename the file extension from .zip to .xpi. Functionally, these files will behave the same. This is the format that Firefox uses to load an extension.
7. Place this new file into the `selenium-crawler` directory, and modify the crawler accordingly. Make sure that the aforementioned `local-crawler.js` file is looking for the correct extension, i.e.,

```js
.addExtensions("ext.xpi");
```

is pointing to the right XPI file.

## 5. Known Issues

### Coordinates and Zip Codes under VPNs

The motivation to use Google Cloud was primarily fueled by this issue. As described in the [privacy pioneer](https://github.com/privacy-tech-lab/privacy-pioneer?tab=readme-ov-file#7-privacy-practice-analysis) repo, the extension is meant to find evidence of location elements being taken. However, when using a VPN (or any service without a static IP), it becomes nearly impossible for privacy pioneer to find evidence of GPS Location and/or Zip Code. This is due to how privacy pioneer decides where the user's [location](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API) is, and so there will almost certainly be a discrepancy between where privacy pioneer thinks the user is, and where a website thinks the user is. Since these features are built-in to the extension, it would be difficult to make privacy pioneer work with a VPN crawl without signifant changes to the architecture. Thus, we have opted to hard-code the latitude, longitude, and zip code for our crawls. For instructions on how to do this, look [here](#22-crawler-setup).

### Cloud Computing Power

We've had issues with Selenium working properly when working with a relatively weak virtual machine. We recommend using the n2-standard-4 preset in Google Cloud.

### Connecting to Cloud VMs

Currently, the only way to actually see the GUI is through the Remote Desktop Connection app on Windows.

### Starting the Crawl

If the crawler fails to start, simply try running it again. Firefox nightly is updated often, and this causes the program to crash on the first bootup. Try running the program in `privacy-pioneer-web-crawler/selenium-crawler` again.

### Other issues

If you encounter an issue that hasn't been described, try to identify if the issue is coming from Selenium or not. To accomplish this, look at any error messages in the terminal that's running in `selenium-crawler`. Make sure that you're connected to the internet, both programs are running, and that the crawler looks as shown [above](#22-crawler-setup).

## 6. Thank You

<p align="center"><strong>We would like to thank our financial supporters!</strong></p><br>

<p align="center">Major financial support provided by Google.</p>

<p align="center">
  <a href="https://research.google/outreach/research-scholar-program/recipients/?category=2022/">
    <img class="img-fluid" src="./google_logo.png" height="80px" alt="Google Logo">
  </a>
</p>

<p align="center">Additional financial support provided by Wesleyan University and the Anil Fernando Endowment.</p>

<p align="center">
  <a href="https://www.wesleyan.edu/mathcs/cs/index.html">
    <img class="img-fluid" src="./wesleyan_shield.png" height="70px" alt="Wesleyan University Logo">
  </a>
</p>

<p align="center">Conclusions reached or positions taken are our own and not necessarily those of our financial supporters, its trustees, officers, or staff.</p>

##

<p align="center">
  <a href="https://privacytechlab.org/"><img src="./plt_logo.png" width="200px" height="200px" alt="privacy-tech-lab logo"></a>
<p>
