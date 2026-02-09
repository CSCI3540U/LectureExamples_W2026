const express = require('express');
const app = express();
const port = 9000;

app.use(express.static('static'));
app.use(express.urlencoded({extended: false}));

app.get('/main', (request, response) => {
    response.send('index');
});

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

app.post('/login', (request, response) => {
    const email = request.body['email'];
    if (Object.keys(loginData).includes(email)) {
        if (request.body['password'] === loginData[email]) {
            // login success
            response.redirect('/main');
        } else {
            // correct username, incorrect password
            response.send(`Password does not match our records for ${email}`);
            return;
        }
    } else {
        // incorrect username, unknown password
        response.send(`Unknown user: ${email}`);
        return;
    }
});

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});