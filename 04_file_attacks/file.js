const express = require('express');
const app = express();
const port = 9000;

const fs = require('fs');
const path = require('path');

const axios = require('axios');

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

app.get('/dir_traversal', (request, response) => {
    const file_name = request.query['file'];
    const file_path = __dirname + '/' + file_name;
    console.log(`Including: ${file_path}`);
    response.setHeader('Content-Type', 'text/html');
    fs.realpath(file_path, (error, resolved_path) => {
        if (error) {
            console.error(error);
            return;
        }
        console.log(`resolved path: ${resolved_path}`);
        if (resolved_path.startsWith(__dirname + 'static')) {
            fs.readFile(file_path, (error, data) => {
                if (error) {
                    console.error(error);
                    return;
                }
                response.send(data);
            });
        } else {
            console.log('Directory traversal!');
            return;
        }
    });
    // alternative fix:
    // response.sendFile(__dirname + file_name);
});

app.get('/remote_file_inclusion', async (request, response) => {
    let url_to_include = request.query['page'];
    try {
        let page_response = await axios.get(url_to_include);
        response.send(page_response.data);
    }
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});