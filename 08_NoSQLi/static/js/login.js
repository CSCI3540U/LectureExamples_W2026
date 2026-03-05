function handleLogin() {
    console.log('handleLogin()...');

    const emailField = document.getElementById('email');
    const passwordField = document.getElementById('password');
    const errorMessage = document.getElementById('errorMessage');

    const email = emailField.value;
    const password = passwordField.value;

    console.log(`email: ${email}`);
    console.log(`password: ${password}`);

    fetch ("http://localhost:9000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email,
            password: password
        }),
    })
    .then((response) => response.json())
    .then((result) => {
        if(result.message === "Success") {
            console.log("You are logged in.");
            errorMessage.innerHTML = 'You are logged in. Go to <a href="/profile">Profile</a>.';
        } else {
            console.log("Please check your login information.");
            errorMessage.innerHTML = 'Please check your login information.  <a href="/login">Try again</a>.';
        }
    });
}
