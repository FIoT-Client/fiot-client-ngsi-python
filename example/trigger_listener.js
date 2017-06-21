var express = require('express');
var app = express();

app.post('/event', function (req, res) {
    res.send('POST /event received!');
    console.log('POST /event received!');
});

app.listen(1234, function () {
    console.log('Simple attribute rule listener on port 1234!');
});
