# privacy-pioneer-web-crawler

A web crawler for detecting websites' data collection and sharing practices at scale.

This crawler requires that [Firefox Nightly](https://www.mozilla.org/en-US/firefox/channel/desktop/) be installed.

## Instructions for setting up mysql on macOS

Install mysql

Once installed, if you're using Homebrew on macOS run

```bash
brew services start mysql
```


Now create a new user by running the following:

```bash
mysql -u root -p
```

Then it'll ask for password and type in `abc`

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'abc';
```

```sql
FLUSH PRIVILEGES;
```

## Instructions for setting up mysql on Windows

Install mysql and the mysql shell

Once installed, enter the shell and run the following commands:

```
\connect root@localhost
```

(enter your root password)

```
\sql
```

To set the crawler up for accessing the database via your root account, run the following command:
```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'abc';
```

```sql
FLUSH PRIVILEGES;
```

## Database Setup

Then create a database by running the following:

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

## Instructions for running the crawler

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

## Important

Every time we want to make a change to Privacy Pioneer for the crawl, we will need to recompile the xpi file. Instructions for this process coming in a later issue. At this point, see issue 541 in PP.
