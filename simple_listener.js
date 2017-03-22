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

app.post('/event', function (req, res) {
    res.send('POST /event received!');
    console.log('POST /event received!');
});

app.get('/event', function (req, res) {
    res.send('GET /event received!');
    console.log('GET /event received!');
});

app.put('/event', function (req, res) {
    res.send('PUT /event received!');
    console.log('PUT /event received!');
});

app.listen(1234, function () {
    console.log('Simple attribute changes listener on port 1234!');
});
