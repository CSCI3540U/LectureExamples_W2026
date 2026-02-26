const crypto = require('crypto');

function hash(password) {
    return crypto.createHash('md5').update(password).digest("hex");
}

const Database = require('better-sqlite3');
const db = new Database(__dirname + '/../data/auth_data.db');

db.exec(`CREATE TABLE IF NOT EXISTS auth_data(userId INTEGER PRIMARY KEY,
                            email TEXT,
                            hashedPw TEXT,
                            role TEXT,
                            firstName TEXT,
                            lastName TEXT)`);
db.exec('DELETE FROM auth_data');
const insert = db.prepare('INSERT INTO auth_data(email, firstName, lastName, hashedPw, role) VALUES(?, ?, ?, ?, ?)');
insert.run('bsmith@abc.com', 'Robert', 'Smith', hash('bobby'), 'user');
insert.run('akhan@abc.com', 'Ahmed', 'Khan', hash('ahmed'), 'user');
insert.run('admin@abc.com', 'Administrator', '', hash('secret123'), 'admin');
console.log('Sample database data added.');

function isEmailAlreadyUsed(email) {
    const users = db.prepare(`SELECT userId FROM auth_data WHERE email = '${email}'`).all();
    //const users = db.prepare('SELECT userId FROM auth_data WHERE email = ?').all(email);
    if (users.length > 0) {
    //if (users.length == 1) {
        return true;
    } else {
        return false;
    }
}

function checkEmailAndPassword(email, password) {
    const user = db.prepare(`SELECT * FROM auth_data WHERE email = '${email}' and hashedPw = '${hash(password)}'`).get();
    //const user = db.prepare(`SELECT * FROM auth_data WHERE email = ? and hashedPw = ?`).get(email, hash(password));
    if (user) {
        return user.userId;
    } else {
        return false;
    }
}

function shutdown() {
    db.close();
}

const syncWait = ms => {
    const end = Date.now() + ms
    while (Date.now() < end) continue
}

module.exports.isEmailAlreadyUsed = isEmailAlreadyUsed;
module.exports.checkEmailAndPassword = checkEmailAndPassword;
module.exports.shutdown =shutdown;
module.exports.syncWait = syncWait;
