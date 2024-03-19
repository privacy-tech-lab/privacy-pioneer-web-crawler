# privacy-pioneer-web-crawler

A web crawler for detecting websites' data collection and sharing practices at scale.

**Note:** Due to problems with detecting location requests when using a VPN, we have decided to continue our crawling on virtual machines in the Google Cloud. The local setup remains the same, but in order to make a cloud VM, there are some extra steps involved.

In the same vein, we have resorted to hard-coding the expected location values in the extension. Instructions for how to do this are located at the bottom of the README.

## Instructions for setting a new VM on Google Cloud

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

## Instructions for setting up the crawler

**This crawler requires that [Firefox Nightly](https://www.mozilla.org/en-US/firefox/channel/desktop/) be installed.**

### Instructions for setting up mysql on macOS

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

### Instructions for setting up mysql on Windows

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

### Database Setup

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

### Instructions for running the crawler

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

## Important: Changing the extension for a crawl

Here are the steps for creating a new version of the extension (this is important because each location will have a different version)

1. In the privacy-pioneer source code, navigate to `src/background/analysis/buildUserData/importSearchDarta.js`
2. Above line 77 (let locKey = ....), set locCoords = [lat, long], where lat and long are the actual latitude and longitude values of the city we are crawling from. This value can be obtained by searching the city on [this website](https://www.latlong.net/)
3. Also above line 77, set retJson.zipCode = zipCodeString, where zipCodeString is your target zip code represented as a string. This value can be obtained by visting websites from our validation sets, observing the ground truth, and identifying common zip code values being taken by websites. This value should be whichever zip code the websites seem to think that we are at.
4. Once the changes have been made, run `npm run build`.
5. Navigate to the `dev` directory.
6. In the `manifest.json` file, add the following code at the bottom (within the json)

```
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
