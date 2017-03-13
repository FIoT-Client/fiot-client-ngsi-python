var express = require('express');
var app = express();

app.post('/', function (req, res) {
  res.send('POST / received!');
  console.log('POST / received!');
});

app.post('/notify', function (req, res) {
  res.send('POST /notify received!');
  console.log('POST /notify received!');
});

app.listen(1234, function () {
  console.log('Simple attribute changes listener on port 1234!');
});
