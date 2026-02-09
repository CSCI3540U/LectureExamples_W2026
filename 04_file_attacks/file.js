const express = require('express');
const app = express();
const port = 9000;
const fileUpload = require('express-fileupload');
const fs = require('fs');
const path = require('path');

const axios = require('axios');

app.use(express.static('static'));
app.use(express.urlencoded({extended: false}));
app.use(fileUpload({
    limits: { fileSize: 25 * 1024 * 1024 },
    abortOnLimit: true,
    useTempFiles: true,
    tempFileDir: '/tmp/',
    safeFileNames: true, // alphanumeric, -, and _
    preserveExtension: true
}));

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
    } catch (error) {
        console.error(`RMI Error: ${error}`);
    }
});

app.post('/file_upload', async (request, response) => {
    const file = request.files.uploaded_image;
    const desired_file_path = path.join(path.join(__dirname, 'uploads'), file.name);
    if (file.name.endsWith('.jpg') && file.mimetype === 'image/jpeg') {
        const cmd = await exec(`file ${file.tempFilePath}`);
        if (cmd.stderr) {
            // handle error
            console.error(`Error executing file command: ${cmd.stderr}`);
            return;
        }
        if (file.stdout.includes('JPEG')) {
            file.mv(desired_file_path, (error) => {
                if (error) {
                    console.log(`Error opening file: ${error}`);
                    return;
                }
                response.statusCode = 200;
                response.setHeader('Content-Type', 'text/html');
                response.write(`File name: ${file.name}<br />`);
                response.write(`File size: ${file.size}<br />`);
                response.write(`File hash: ${file.md5}<br />`);
                response.write(`MIME type: ${file.mimetype}<br />`);
                response.write(`Temp path: ${file.tempFilePath}<br />`);
                response.write(`Dest path: ${desired_file_path}<br />`);
                response.end();
            });
        }
    }
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});