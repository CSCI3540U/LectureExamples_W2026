const express = require('express');
const app = express();
const port = 9000;

// middleware
app.use(express.static('static'));
app.use(express.urlencoded({extended: false}));

// routes
app.get('/index', (request, response) => {
    response.send('<h1>index page</h1>');
});

app.get('/login', (request, response) => {
    console.log(request.query);
    response.send(`/login GET ${request.query['username']}`);
});

app.post('/login', (request, response) => {
    console.log(request.body);
    response.send(`/login POST ${request.body['username']}`);
});

app.get('/posts/:category/:postid', (request, response) => {
    console.log(request.params);
    response.send(`/posts GET ${request.params['category']}`);
});

app.listen(port, () => {
    console.log(`Listening on port ${port}.`);
});
