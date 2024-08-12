document.addEventListener('DOMContentLoaded', async () => {
    
    checkAuthentication();
    
    const token = getCookie('token');
    const categorySidebarCheckbox = document.getElementById('sidebar-active');
    const itemsSidebarCheckbox = document.getElementById('items-sidebar-active');

    // Handling sign-up form submission
    const signUpForm = document.getElementById('signup-form');

    if (signUpForm) {
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
    }

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

    // Populate the sidebar with categories
    if (token) {
        const categoriesList = document.querySelector('.category-list');

        if (categoriesList) {
            const categories = await fetchCategories(token);

            categories.forEach(category => {
                const li = document.createElement('li');
                li.textContent = category.name;

                // Showing the respective item sidebar depending on the category clicked
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `category-${category.name}`;
                checkbox.style.display = 'none';
                li.prepend(checkbox);

                li.addEventListener('click', async () => {
                    const items = await fetchCategoryItems(category.name);
                    itemsSidebarCheckbox.checked = true;
                    displayItems(items);
                });
                categoriesList.appendChild(li); // Displaying categories on the sidebar
            });
        }
    }

    categorySidebarCheckbox.addEventListener('change', () => {
        if (!categorySidebarCheckbox.checked) {
            itemsSidebarCheckbox.checked = false;  // Close item sidebar if category sidebar is closed
        }
    });

    const createListButton = document.getElementById('create-list-button');

    createListButton.addEventListener('click', async () => {
        const shoppingListId = await createShoppingList();
        if (shoppingListId) {
            console.log(`Shopping list created with ID: ${shoppingListId}`);
        }
    });
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
        loginLink.style.display = token ? 'none' : 'inline-block';
    }

    if (logoutButton) {
        logoutButton.style.display = token ? 'inline-block' : 'none';
        logoutButton.addEventListener('click', logoutUser);
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

// Function to fetch all categories
async function fetchCategories(token) {
    try {
        const response = await fetch('http://127.0.0.1:5000/categories', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const categories = await response.json();
            return categories;
        }
        else {
            displayErrorMessage(`HTTP error! status: ${response.statusText}`);
        }
    }
    catch (error) {
        console.error('Error fetching categories:', error);
        return [];
    }
}

// Function to fetch all the items of a category clicked
async function fetchCategoryItems(categoryName) {
    const token = getCookie('token');

    try {
        const response = await fetch(`http://127.0.0.1:5000/categories/${categoryName}/items`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const items = await response.json();
            return items
        }
        else {
            displayErrorMessage(`HTTP error! status: ${response.statusText}`);
        }
    }
    catch (error) {
        console.error('Error fetching items:', error);
        return [];
    }
}

// Function to display category items in the sidebar
function displayItems(items)  {
    const itemsList = document.querySelector('.category-items-list');
    itemsList.innerHTML = '';

    items.forEach(item => {
        const itemElement = document.createElement('li');
        itemElement.textContent = item.name;

        itemElement.addEventListener('click', () => {
            addItemToShoppingList(item.id);
            displayShoppingListItems([item]);
        });

        itemsList.appendChild(itemElement);
    });
}

async function createShoppingList() {
    const token = getCookie('token');

    try {
        const response = await fetch('http://127.0.0.1:5000/shopping_lists', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name: 'My Shopping List' })
        });

        if(response.ok) {
            const data = await response.json();
            return data.id;
        }
        else {
            console.error('Failed to create shopping list:', response.statusText)
        }
    }
    catch (error) {
        console.error('Error creating shopping list:', error);
    }
}

async function addItemToShoppingList(itemId) {
    const token = getCookie('token');
    let shoppingListId = localStorage.getItem('shoppingListId');

    if(!shoppingListId) {
        shoppingListId = await createShoppingList();
        localStorage.setItem('shoppingListId', shoppingListId);
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/shopping_lists/${shoppingListId}/items`, {
            method: 'POST',
            method: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ item_id: itemId })
        });

        if (response.ok) {
            alert('Item added to shopping list!');
        }
        else {
            console.error('Failed to add item:', response.statusText);
        }
    }
    catch (error) {
        console.error('Error adding item to shopping list:', error);
    }

}

function displayShoppingListItems(items) {
    const shoppingListItems = document.querySelector('.shopping-list-items');

    items.forEach(item => {
        const itemElement = document.createElement('li');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = 'shopping-list-checkbox'
        checkbox.addEventListener('change', () => {
            itemElement.style.textDecoration = checkbox.checked ? 'line-through' : 'none';
        });

        const label = document.createElement('label');
        label.textContent = item.name;

        itemElement.appendChild(label);
        itemElement.appendChild(checkbox);

        shoppingListItems.appendChild(itemElement);
    });
}
