const express = require('express');
const app = express();
const port = 9000;

const session = require('express-session');
const cookieParser = require('cookie-parser')

const Database = require('better-sqlite3');
const db = new Database(__dirname + 'auth_data.db');

const auth_model = require('./models/auth_model.js');

// middleware
app.use(express.static('www'));
app.use(express.urlencoded({extended: false}));
app.use(cookieParser());
app.use(session({
   resave: false,
   saveUninitialized: false,
   secret: 'the giraffe with its long neck is able to reach the highest branches'
}));
app.set('views', __dirname + '/views');
app.set('view engine', 'pug');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

app.get('/home', (request, response) => {
    let email = request.session['email'];
    let role = request.session['role'];
    if (email) {
       response.send(`Welcome, ${email} (role: ${role}).<br /><a href="/logout">Logout</a>`);
    } else {
       response.redirect('/login');
    }
 });

app.get('/login', function(request, response) {
    response.render('login', {
       title: 'Login Page',
       errorMessage: ''
    });
 });

 app.post('/processLogin', function(request, response) {
    sleep(500).then(() => { 
       let checkResult = auth_model.checkEmailAndPassword(request.body.email, request.body.password);
       if (checkResult) {
          request.session['email'] = request.body.email;
          request.session['role'] = 'user';
 
          response.redirect('/home');
          return;
       }
       // no such email or incorrect password
       response.status(401).render('login', {
          title: 'Login Page',
          errorMessage: 'Login incorrect'
       });
    });
 });
 
 app.get('/logout', (request, response) => {
    request.session.email = '';
    request.session.role = '';
 
    response.redirect('/login');
 });

 app.listen(port, () => {
    console.log(`Web server listening on port ${port}`);
 });