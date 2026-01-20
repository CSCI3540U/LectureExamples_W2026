const express = require('express');
const app = express();
const port = 9000;
const cookieParser = require('cookie-parser');

// middleware
app.use(express.static('static'));
app.use(express.urlencoded({extended: false}));
app.use(cookieParser());

let lastSessionId = 1000000;

let sessionData = {};

// routes
app.get('/index', (request, response) => {
    const sessId = request.cookies['session-id'];
    response.send(`<h1>index page (Session ID: ${sessId})</h1>`);
});

app.get('/login', (request, response) => {
    console.log(request.query);
    response.send(`/login GET ${request.query['username']}`);
});

app.post('/login', (request, response) => {
    // console.log(request.body);
    // response.send(`/login POST ${request.body['username']}`);
    const sessId = `${lastSessionId++}`;

    sessionData[sessId] = request.body.username;

    response.cookie('session-id', sessId, {
        /*secure: true,*/
        httpOnly: true,
        path: '/'
    });

    response.redirect('/index');
});

app.get('/posts/:category/:postid', (request, response) => {
    console.log(request.params);
    response.send(`/posts GET ${request.params['category']}`);
});

app.listen(port, () => {
    console.log(`Listening on port ${port}.`);
});
