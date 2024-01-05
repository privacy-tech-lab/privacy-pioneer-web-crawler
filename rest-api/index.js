require("dotenv").config();

const express = require("express");

const bodyParser = require("body-parser");
const connection = require("./database.js");
const app = express();
var debug = false;

const args = process.argv;
if (args.length > 2 && args[2] == "debug") {
  console.log("using debugging version!");
  debug = true;
}

async function rest(table) {
  // create application/json parser
  var jsonParser = bodyParser.json();

  // set table name
  const table_name = "entries";

  app.get("/", (req, res) => res.send("Try: /" + table));

  app.get("/status", (req, res) => res.send("Success."));

  app.get("/" + table_name, (req, res) => {
    connection.query(
      "SELECT * FROM ??.??",
      [process.env.DB_DATABASE, table_name],
      (error, results, fields) => {
        if (error) throw error;
        res.json(results);
      }
    );
  });

  // CREATE TABLE entries (id INTEGER PRIMARY KEY AUTO_INCREMENT, timestp text(255), permission text(255), rootUrl text(6000), snippet text(6000), requestUrl text(6000), typ text(255), ind text(255), firstPartyRoot varchar(255), parentCompany text(255), watchlistHash text(255), extraDetail text(255), cookie varchar(255), loc varchar(255));

  app.post("/" + table_name, jsonParser, (req, res) => {
    // console.log(req.body);
    const reqBody = req.body;
    if (reqBody == {}) {
      res.json({ res: "empty body" });
    } else {
      console.log(reqBody.host);
      const evidence = reqBody.evidence;
      for (const [label, value] of Object.entries(evidence)) {
        if (label != "lastSeen") {
          for (const [type, requests] of Object.entries(value)) {
            for (const [url, e] of Object.entries(requests)) {
              var timestamp = e.timestamp;
              var permission = e.permission;
              var rootUrl = e.rootUrl;
              var snippet = e.snippet;
              var requestUrl = e.requestUrl;
              var typ = e.typ;
              var index = e.index;
              var firstPartyRoot = e.firstPartyRoot;
              var parentCompany = e.parentCompany;
              var watchlistHash = e.watchlistHash;
              var extraDetail = e.extraDetail;
              var cookie = e.cookie;
              var loc = e.loc;
              // console.log("posting to analysis...");
              connection.query(
                "INSERT INTO ??.?? (timestp, permission, rootUrl, snippet, requestUrl, typ, ind, firstPartyRoot, parentCompany, watchlistHash, extraDetail, cookie, loc) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                  process.env.DB_DATABASE,
                  table_name,
                  timestamp,
                  permission,
                  rootUrl,
                  snippet,
                  requestUrl,
                  typ,
                  index,
                  firstPartyRoot,
                  parentCompany,
                  watchlistHash,
                  extraDetail,
                  cookie,
                  loc,
                ],
                (error, results, fields) => {
                  if (error) throw error;
                  // console.log(results)
                }
              );
            }
          }
        }
      }
      res.json({ res: "completed" });
    }
  });
}

rest("analysis");

// Use port 8080 by default, unless configured differently in Google Cloud
const port = process.env.PORT || 8080;
app.listen(port, () => {
  console.log(`App is running at: http://localhost:${port}`);
});
