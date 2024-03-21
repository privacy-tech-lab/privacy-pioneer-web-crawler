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

A web crawler for detecting websites' data collection and sharing practices at scale using [Privacy Pioneer](https://github.com/privacy-tech-lab/privacy-pioneer).

**Note:** Due to problems with detecting location requests when using a VPN, we have decided to continue our crawling on virtual machines with Google Cloud. The local setup remains the same, but in order to make a cloud VM, there are some extra steps involved.

In the same vein, we have resorted to hard-coding the expected location values in the extension. Instructions for how to do this are located at the bottom of the README.

The code in this repo is developed and maintained by the [Privacy Pioneer team](https://github.com/privacy-tech-lab/privacy-pioneer#privacy-pioneer).

## 1. Instructions for Creating a New VM on Google Cloud

Before you can set up on the cloud, you need to create a virtual machine.

**Note:** Anyone with access is able to make / modify the machines through the Google Cloud console, but the only way at the moment to actually use the VM GUI is through the Remote Desktop Connection app on Windows.

1. Go to the privacy-pioneer-web-crawler project (you will need access to this)
2. Select _Compute Engine_
3. Select _Create Instance_
4. Select _Create from Machine Image_. This will make it so that all the software / settings will be identical to the template that has been made.
5. Rename the VM to whatever location it will be representing.
6. Scroll down and choose the appropriate region.
7. Create the VM.
8. Now, in the _VM Instances_ menu, click on the little triangle next to RDP. Click on Set Windows Password. **SAVE THE USERNAME AND PASSWORD SOMEWHERE SECURE!!! THEY WILL ONLY BE SHOWN ONCE**.
9. Once you have those credentials, and the VM is running, you should be able to connect using the external IP (listed in the _VM instances_ menu)

## 2. Instructions for Setting up the Crawler

**Note:** The crawler requires that [Firefox Nightly](https://www.mozilla.org/en-US/firefox/channel/desktop/) be installed

### 2.1 Instructions for Setting up MySQL on macOS

Install MySQL. Once installed, if you are using Homebrew on macOS run:

```bash
brew services start mysql
```

Now, create a new user:

```bash
mysql -u root -p
```

Then, you will be asked for a password. Type in `abc`:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'abc';
```

```sql
FLUSH PRIVILEGES;
```

### 2.2 Instructions for Setting up MySQL on Windows

Install MySQL and the MySQL shell. Once installed, enter the shell and run the following commands:

```bash
\connect root@localhost
```

Enter your root password.

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

### 2.3 Database Setup

Then, create a database:

```sql
CREATE DATABASE analysis;
```

```sql
USE analysis;
```

```sql
CREATE TABLE entries (id INTEGER PRIMARY KEY AUTO_INCREMENT, timestp varchar(255), permission varchar(255), rootUrl varchar(255), snippet varchar(4000), requestUrl varchar(4000), typ varchar(255), ind varchar(255), firstPartyRoot varchar(255), parentCompany varchar(255), watchlistHash varchar(255), extraDetail varchar(255), cookie varchar(255), loc varchar(255));
```

Then, in `rest-api`, create a new file called `.env`, and save the following to that file:

```bash
DB_CONNECTION=mysql
DB_HOST=localhost
DB_DATABASE=analysis
DB_USERNAME=root
DB_PASSWORD=abc
```

## 3. Instructions for Running the Crawler

If using Windows, navigate to `privacy-pioneer-web-crawler/selenium-crawler/local-crawler.js` and alter the command

```js
.setBinary("...")
```

under the function `setup()` to refer to the correct path to your Firefox Nightly binary, likely `C:\Program Files\Firefox Nightly\firefox.exe`

1. Enter the `privacy-pioneer-web-crawler/rest-api` directory, and run either:

   ```bash
   npm install
   node index.js
   ```

   or

   ```bash
   npm install
   npm start
   ```

2. In another terminal, enter the `privacy-pioneer-web-crawler/selenium-crawler` directory, and run either:

   ```bash
   npm install
   node local-crawler.js
   ```

   or

   ```bash
   npm install
   npm start
   ```

These two commands are enough to get the crawl to run.

## 4. Important: Changing the Extension for a Crawl

Here are the steps for creating a new version of the extension (this is important because each location will have a different version)

1. In the privacy-pioneer source code, navigate to `src/background/analysis/buildUserData/importSearchDarta.js`
2. Above line 77 (let locKey = ....), set locCoords = [lat, long], where lat and long are the actual latitude and longitude values of the city we are crawling from. This value can be obtained by searching the city on [this website](https://www.latlong.net/)
3. Also above line 77, set retJson.zipCode = zipCodeString, where zipCodeString is your target zip code represented as a string. This value can be obtained by visiting websites from our validation sets, observing the ground truth, and identifying common zip code values being taken by websites. This value should be whichever zip code the websites seem to think that we are at.
4. Once the changes have been made, run `npm run build`.
5. Navigate to the `dev` directory.
6. In the `manifest.json` file, add the following code at the bottom (within the json)

   ```json
   "browser_specific_settings": {
       "gecko": {
         "id": "{daf44bf7-a45e-4450-979c-91cf07434c3d}"
       }
     }
   ```

7. Take all the files in the `dev` directory and compile them as a zip file.
8. Change the file from .zip to .xpi (just rename it)
9. Place this new file into the web crawler directory, and modify the crawler accordingly.

Every time we want to make a change to Privacy Pioneer for the crawl, we will need to recompile the xpi file. Instructions for this process coming in a later issue. At this point, see issue 541 in PP.

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
