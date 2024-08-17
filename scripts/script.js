let selectedItems = [];

document.addEventListener('DOMContentLoaded', async () => {
    
    checkAuthentication();
    
    const token = getCookie('token');
    const categorySidebarCheckbox = document.getElementById('sidebar-active');
    const itemsSidebarCheckbox = document.getElementById('items-sidebar-active');
    const selectedItemsSidebar = document.getElementById('selected-items-sidebar');
    
    const shoppingListId = localStorage.getItem('shoppingListId');
    const shoppingListContainer = document.getElementById('shopping-list-container');

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

    itemsSidebarCheckbox.addEventListener('change', () => {
        if (itemsSidebarCheckbox.checked) {
            selectedItemsSidebar.classList.add('active');
        }
        else {
            selectedItemsSidebar.classList.remove('active');
        }
    })

    const createListButton = document.getElementById('create-list-button');

    createListButton.addEventListener('click', async () => {
        const newListId = await createShoppingList();
        if (newListId) {
            localStorage.setItem('shoppingListId', newListId);
            console.log('Shopping List created successfully!');
            shoppingListContainer.classList.remove('hidden');
            createListButton.style.display = 'none';
            submitButton.style.display = 'block';
            deleteListButton.style.display = 'blocke';
            document.getElementById('submit-items-button').disabled = false;
        }
    });

    const submitButton = document.getElementById('submit-items-button');
    submitButton.addEventListener('click',  () => {
        addItemToShoppingList();
    });

    if(!localStorage.getItem('shoppingListId')) {
        submitButton.disabled = true;
    }

    const deleteListButton = document.getElementById('delete-list-button');
    deleteListButton.addEventListener('click', async () => {
        const shoppingListId = localStorage.getItem('shoppingListId');
        if (shoppingListId) {
            await deleteShoppingList(shoppingListId);
            localStorage.removeItem('shoppingListId');
            clearShoppingListItems();
        }
    });

    if (shoppingListId) {
        await fetchShoppingListById(shoppingListId);
        shoppingListContainer.classList.remove('hidden');
        createListButton.style.display = 'none';
        submitButton.style.display = 'block';
        deleteListButton.style.display = 'blocke';
    } else {
        submitButton.style.display = 'none';
        deleteListButton.style.display = 'none';
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
    const selectedItemsSidebar = document.getElementById('selected-items-sidebar');
    itemsList.innerHTML = '';
    
    items.forEach(item => {
        const itemElement = document.createElement('li');
        itemElement.textContent = item.name;
        
        itemElement.addEventListener('click', () => {
            if (!selectedItems.some(selectedItems => selectedItems.id === item.id)) {
                selectedItems.push(item);
                selectedItemsSidebar.classList.remove('hidden');
                displaySelectedItems();
            }
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

async function addItemToShoppingList() {

    const token = getCookie('token');
    let shoppingListId = localStorage.getItem('shoppingListId');

    if (!shoppingListId) {
        alert('Please create a shopping list first')
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/shopping_lists/${shoppingListId}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ item_ids: selectedItems.map(item => item.id) })
        });

        if (response.ok) {
            const data = await response.json();
            selectedItems = [];
            displaySelectedItems();
            document.getElementById('selected-items-sidebar').classList.add('hidden');
        }


    } 
    catch (error) {
        console.error('Error adding item to shopping list:', error);
    }
}

function displaySelectedItems() {
    const selectedItemsContainer = document.querySelector('.selected-items-list');
    selectedItemsContainer.innerHTML = '';

    selectedItems.forEach(item => {
        const itemElement = document.createElement('li');
        itemElement.textContent = `${item.name}`;

        selectedItemsContainer.appendChild(itemElement);
    });
}

async function fetchShoppingListById(shoppingListId) {
    const token = getCookie('token');
    
    try {
        const response = await fetch(`http://127.0.0.1:5000/shopping_lists/${shoppingListId}/items`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const items = await response.json();
            displayShoppingListItems(items); // Display the items
        } else {
            console.error('Failed to fetch shopping list:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching shopping list:', error);
    }
}

function displayShoppingListItems(items) {
    const shoppingListId = localStorage.getItem('shoppingListId');
    const shoppingListItems = document.querySelector('.shopping-list-items');
    shoppingListItems.innerHTML = '';  // Clear existing items

    items.forEach(item => {
        const itemElement = document.createElement('li');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = item.checked;  // Set the checkbox status based on the fetched data
        checkbox.id = 'shopping-list-checkbox';
        checkbox.addEventListener('change', () => {
            itemElement.style.textDecoration = checkbox.checked ? 'line-through' : 'none';
            updateItemStatus(item.id, checkbox.checked);  // Update status in the backend
        });

        const label = document.createElement('label');
        label.textContent = item.name;

        itemElement.appendChild(label);
        itemElement.appendChild(checkbox);

        shoppingListItems.appendChild(itemElement);
    });
}

async function updateItemStatus(itemId, checkedStatus) {
    const token = getCookie('token');

    try {
        const response = await fetch(`http://127.0.0.1:5000/shopping_lists/items/${itemId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ checked: checkedStatus })
        });

        if (!response.ok) {
            console.error('Failed to update item status:', response.statusText);
        }
    } catch (error) {
        console.error('Error updating item status:', error);
    }
}


function clearShoppingListItems() {
    const shoppingListItems = document.querySelector('.shopping-list-items');
    shoppingListItems.innerHTML = '';
}

async function deleteShoppingList(shoppingListId) {
    const token = getCookie('token');

    try {
        const response = await fetch(`http://127.0.0.1:5000/shopping_lists/${shoppingListId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            console.log('Shopping list deleted successfully.');
        }
        else {
            console.error('Failed to delete shopping list:', response.statusText);
        }
    }
    catch (error) {
        console.error('Error deleting shopping list:', error);
    }
}
