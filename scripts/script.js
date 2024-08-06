document.addEventListener('DOMContentLoaded', () => {

    const token = getCookie('token');

    // Handling sign-up form submission
    const signUpForm = document.getElementById('signup-form');

    signUpForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        };

        // TODO: Validate formData before sending it

        try {
            const response = await createUser(formData);

            if (response.status === 201) {
                alert('Account created succesfully!')
                window.location.href = 'login.html';
            }
            else {
                if (response.headers.get('Content-Type').includes('application/json') && response.body) {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.message}`);
                }
                else {
                    displayErrorMessage('An error occurred while creating your account: ' + response.statusText);
                }
            }
        }
        catch (error) {
            displayErrorMessage('An error ocurred: ' + error.message);
        }
    });

    // Handling login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await loginUser(email, password);
                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/`;
                    window.location.href = 'index.html';
                }
                else {
                    displayErrorMessage('Login failed: ' + response.statusText);
                }
            }
            catch (error) {
                displayErrorMessage('An error ocurred: ' + error.message);
            }
        });
    }
});

async function createUser(formData) {
    const response = await fetch('http://127.0.0.1:5000/users/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    });

    return response;
}

// Function to check if user is authenticated and adjust the UI accordingly
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    const logoutButton = document.getElementById('logout-button');

    if (loginLink) {
        loginLink.style.display = token ? 'none' : 'inline-block'
    }

    if (logoutButton) {
        logoutButton.style.display = token ? 'inline-block' : 'none';
    }
}

// Function to retrieve the value of a cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Function to log in user and retrieve authentication token
async function loginUser(email, password) {
    const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password})
    });
    return response;
}

// Function to display error messages
function displayErrorMessage(message) {
    const errorMessage = document.getElementById('error-messgae');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Function to log out user
function logoutUser() {
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    window.location.href = 'login.html';
}
