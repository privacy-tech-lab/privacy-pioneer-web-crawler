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

The crawler requires that [Firefox Nightly](https://www.mozilla.org/en-US/firefox/channel/desktop/) be installed.

The code in this repo is developed and maintained by the [Privacy Pioneer team](https://github.com/privacy-tech-lab/privacy-pioneer#privacy-pioneer).

## 1. Instructions for Setting up MySQL on macOS

Install MySQL. Once installed, if you are using Homebrew on macOS run:

```bash
brew services start mysql
```

Now, create a new user by running:

```bash
mysql -u root -p
```

Then, you will be asked for a password. You can type in `abc`:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'abc';
```

```sql
FLUSH PRIVILEGES;
```

## 2. Instructions for Setting up MySQL on Windows

Install MySQL and the MySQL shell. Once installed, enter the shell and run:

```bash
\connect root@localhost
```

Now, enter your root password.

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

## 3. Database Setup

Then, create a database by running:

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

## 4. Instructions for Running the Crawler

If you are using Windows, navigate to `privacy-pioneer-web-crawler/selenium-crawler/local-crawler.js` and alter the command

```js
.setBinary("...")
```

under the function `setup()` to refer to the correct path to your Firefox Nightly binary, likely `C:\Program Files\Firefox Nightly\firefox.exe`.

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

## 5. Important Note

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
