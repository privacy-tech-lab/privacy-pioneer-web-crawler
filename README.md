# privacy-pioneer-web-crawler

A web crawler for detecting websites' data collection and sharing practices at scale

## Instructions for setting up the mysql database

Install and enter mysql.

Create a new user and make sure that the password is `abc`.

Run

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
DB_USERNAME=<the username you provided to mysql>
DB_PASSWORD=abc
```

## Instructions for running the crawler

1. Enter the `privacy-pioneer-web-crawler/rest-api` directory, and run either:

   ```bash
   node index.js
   ```

   or

   ```bash
   npm start
   ```

2. In another terminal, enter the `privacy-pioneer-web-crawler/selenium-crawler` directory, and run either:

  ```bash
  node local-crawler.js
  ```

  or

  ```bash
  npm start
  ```

These two commands are enough to get the crawl to run.

## Important

Every time we want to make a change to Privacy Pioneer for the crawl, we will need to recompile the xpi file. Instructions for this process coming in a later issue. At this point, see issue 541 in PP.
