const express = require('express');
const app = express();
const port = 9000;

const fs = require('fs');
const path = require('path');

app.use(express.static('static'));

app.get('/open_redirect', (request, response) => {
    const file_name = request.query['dest'];
    response.redirect(file_name);
});

app.get('/local_file_inclusion', (request, response) => {
    const file_name = request.query['file'];
    response.setHeader('Content-Type', 'text/html');
    response.sendFile(__dirname + `/${file_name}.php`);
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});