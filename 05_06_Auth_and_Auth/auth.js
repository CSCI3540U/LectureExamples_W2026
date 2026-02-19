const express = require('express');
const app = express();
const session = require('express-session');
const cookieParser = require('cookie-parser')
const port = 9000;

let nextSessionId = 2;

let sessionData = {
   '1': {
      'email': 'admin@abc.com',
      'role': 'administrator',
   },
};

const loginData = {
    'admin@xyzhappy.com': 'openup',
    'rhonda.smith@xyzhappy.com': 'shoot and score',
    'hiroshi.tanaka@xyzhappy.com': 'mountain hiker 42',
    'fatima.al-sayed@xyzhappy.com': 'starlit sky',
    'kwame.mensah@xyzhappy.com': 'blue velvet sofa',
    'priya.sharma@xyzhappy.com': 'coffee first always',
    'mateo.rodriguez@xyzhappy.com': 'rainy day vibes',
    'chen.wei@xyzhappy.com': 'pixel perfect 88',
    'amara.diop@xyzhappy.com': 'vintage camera',
    'santiago.lopez@xyzhappy.com': 'desert breeze',
    'anika.bakshi@xyzhappy.com': 'hidden forest',
    'lars.nielsen@xyzhappy.com': 'silver bicycle'
};

function userExists(toFind) {
   return Object.keys(loginData).includes(toFind);
}

function checkPassword(email, password) {
   return loginData[email] === password;
}

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

app.get('/home', (request, response) => {
   console.log(request.cookies);
   let sessionId = request.cookies['session_id'];
   let email = sessionData[sessionId]['email'];
   let role = sessionData[sessionId]['role'];
   if (email) {
      response.send(`Welcome, ${email}! Role: ${role}<br /><a href="/logout">Logout</a>`);
   } else {
      response.redirect('/login');
   }
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
 
app.get('/login', function(request, response) {
    response.render('login', {
       title: 'Login Page',
       errorMessage: ''
    });
});
 
app.post('/processLogin', function(request, response) {
    let email = request.body.email;
    let password = request.body.password;
 
    sleep(500).then(() => { 
       if (userExists(email)) {
          if (checkPassword(email, password)) {
             response.cookie('session_id', `${nextSessionId}`);
             sessionData[nextSessionId] = {email: email, role: 'user'};
             nextSessionId++;
    
             response.redirect('/home');
          } else {
             // password does not match
             response.status(401).render('login', {
                title: 'Login Page',
                errorMessage: 'Login incorrect'
             });
          }
       } else {
          // no such email
          response.status(401).render('login', {
             title: 'Login Page',
             errorMessage: 'Login incorrect'
          });
       }
    });
});

app.get('/logout', (request, response) => {
   request.session.email = '';

   response.redirect('/login');
});

app.listen(port, () => {
   console.log(`Web server is now listening on port ${port}`);
});
