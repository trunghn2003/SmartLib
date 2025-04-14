
//-- notification --

const notification_Button = document.getElementById('notification');
const dropdown_notification = document.getElementById('notification_dropdown');
let closeTimeout_notification;  // Declare this variable at the start to handle the timeout properly
const notificationImg = document.getElementById('img_notification');

// Function to show the dropdown
function showDropdown_notification() {
    clearTimeout(closeTimeout_notification);  // Cancel any scheduled closing
    dropdown_notification.style.display = 'block';
    notificationImg.src='/static/images/empty_notification_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_notification() {
    closeTimeout_notification = setTimeout(() => {
        dropdown_notification.style.display = 'none';
        notificationImg.src='/static/images/empty_notification.png';
    }, 200);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
document.addEventListener('DOMContentLoaded', () => {
    notification_Button.addEventListener('mouseenter', () => {
    showDropdown_notification();
    const empty_notification = document.getElementById('empty_notification');
    const notEmpty_notification = document.getElementById('notEmpty_notification');

    empty_notification.style.display = 'block';
    notEmpty_notification.style.display = 'none';

    const notification_1 = document.getElementById('notifi-item_1');
    const notification_2 = document.getElementById('notifi-item_2');
    const notification_3 = document.getElementById('notifi-item_3');
    

    notification_1.style.display = 'none';
    notification_2.style.display = 'none';
    notification_3.style.display = 'none';

    

    // Fetch initial data when page loads
    fetch(`/adminpanel/api/last-three-pending-books`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch notification');
            }
            return response.json();
        })
        .then(data => {
            if(Array.isArray(data) && data.length === 0){
                empty_notification.style.display = 'block';
                notEmpty_notification.style.display = 'none';
            }
            else if(data){
                empty_notification.style.display = 'none';
                notEmpty_notification.style.display = 'block';

                data.forEach((notification, index) => {
                    const notifi_title = document.getElementById(`notifi-item_title_${index + 1}`);
                    const notifi_content = document.getElementById(`notifi-item_content_${index + 1}`);
                    const notifi_image=document.getElementById(`notifi-item_image_${index + 1}`);
                    const notifi_item = document.getElementById(`notifi-item_${index + 1}`);
            
                    // If there is data for the notification, display the notification item
                    if (notification) {
                        notifi_item.style.display = 'flex'; // Make the notification item visible
            
                        // notification notification details
                        notifi_title.textContent = "Request Upload Book";
                        notifi_content.textContent = notification.book_name+" ,"+notification.book_author || 'No content...';
                        notifi_image.src='/static/images/notfi_upload.png';
                        
                    } else {
                        // If no data for the notification, hide the book item
                        notifi_item.style.display = 'none';
                    }
                });
                
            }
            
        })
        .catch(error => {
            console.error('Error fetching notification:', error);
        });
    
    });
    
});

document.getElementById('viewAll_notification').addEventListener('click', (event) => {
    event.preventDefault();

    window.location.href = '/adminpanel/notifications/';
});

// Event listener for when mouse leaves the categories button
notification_Button.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdown_notification.contains(event.relatedTarget)) {
        hideDropdown_notification();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_notification.addEventListener('mouseenter', () => {
    showDropdown_notification();
});

// Event listener for when mouse leaves the dropdown
dropdown_notification.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!notification_Button.contains(event.relatedTarget)) {
        hideDropdown_notification();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_notification(notification) {
    dropdown_notification.style.display = 'none';  // Hide dropdown after selection
}
//---------------------------------------------------------------------------------------
//-- user --

const userButton = document.getElementById('user');
const dropdown_user = document.getElementById('dropdown-user');
let closeTimeout_user;  // Declare this variable at the start to handle the timeout properly
const userImg = document.getElementById('img_user');

// Function to show the dropdown
function showDropdown_user() {
    clearTimeout(closeTimeout_user);  // Cancel any scheduled closing
    dropdown_user.style.display = 'block';
    userImg.src = '/static/images/user_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_user() {
    closeTimeout_user = setTimeout(() => {
        dropdown_user.style.display = 'none';
        userImg.src = '/static/images/user.png';
    }, 200);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
userButton.addEventListener('mouseenter', () => {
    showDropdown_user();
});

// Event listener for when mouse leaves the categories button
userButton.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdown_user.contains(event.relatedTarget)) {
        hideDropdown_user();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_user.addEventListener('mouseenter', () => {
    showDropdown_user();
});

// Event listener for when mouse leaves the dropdown
dropdown_user.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!userButton.contains(event.relatedTarget)) {
        hideDropdown_user();
    }
});


function loadCategories() {
    fetch('/adminpanel/categories/', { cache: 'no-store' }) 
        .then(response => response.json())
        .then(data => {
            const categoryList = document.getElementById('categoryList');
            categoryList.innerHTML = ''; 

            if (data.categories && data.categories.length > 0) {
                data.categories.forEach(category => {
                    const listItem = document.createElement('li');
                    listItem.innerHTML = `
                        <input type="checkbox" class="category-select" data-id="${category.category_id}">
                        ${category.category_name}
                    `;
                    categoryList.appendChild(listItem);
                });
            } else {
                categoryList.innerHTML = '<li>No categories available.</li>';
            }
        })
        .catch(error => console.error('Error loading categories:', error));
}


function filterCategories() {
    const query = document.getElementById('searchCategory').value.toLowerCase();
    const categoryList = document.getElementById('categoryList').getElementsByTagName('li');
    
    Array.from(categoryList).forEach(category => {
        const text = category.textContent.toLowerCase();
        category.style.display = text.includes(query) ? '' : 'none';
    });
}


function addCategory(event) {
    event.preventDefault();

    const newCategory = document.getElementById('newCategory').value.trim();

    if (!newCategory) {
        return;
    }

    fetch('/adminpanel/add-category/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ category_name: newCategory }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload(); 
        } else if (data.message === 'Category already exists.') {
            alert('This category already exists in the database.');
        } else {
        }
    })
    .catch(error => {
        console.error('Error adding category:', error);
    });
}



function deleteSelectedCategories() {
    const selectedCategories = document.querySelectorAll('.category-select:checked'); 
    const categoryIds = Array.from(selectedCategories)
        .map(checkbox => checkbox.getAttribute('data-id')) 
        .filter(id => id); 

    if (categoryIds.length === 0) {
        return;
    }

    if (!confirm('Are you sure you want to delete the selected categories?')) return;

    fetch('/adminpanel/delete-categories/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ category_ids: categoryIds }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            selectedCategories.forEach(checkbox => {
                const listItem = checkbox.closest('li');
                listItem.remove();
            });
        } else {
        }
    })
    .catch(error => {
        console.error('Error deleting categories:', error);
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split("; ");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function setActive(button) {
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.sidebar button');
    buttons.forEach(btn => btn.classList.remove('active'));

    // Add active class to the clicked button
    button.classList.add('active');

    // Use a small timeout to ensure the class is applied before the redirection
    setTimeout(() => {
        window.location.href = button.getAttribute('data-url');
    }, 50);
}
function handleOptionClick_user(element, option) {
    // Remove 'active' class from all list items
    const items = document.querySelectorAll('.dropdown-user li');
    items.forEach(item => item.classList.remove('active'));

    // Add 'active' class to the clicked list item
    element.classList.add('active');

    // Redirect based on the selected option
    switch (option) {
        case 'Categories Database':
            window.location.href = 'http://127.0.0.1:8000/adminpanel/categories/';
            break;
        case 'User Details':
            window.location.href = 'http://127.0.0.1:8000/adminpanel/user-details/';
            break;
        case 'View Feedback':
            window.location.href = 'http://127.0.0.1:8000/adminpanel/feedback/';
            break;
        case 'Notification':
            window.location.href = 'http://127.0.0.1:8000/adminpanel/notifications/';
            break;
        case 'Book Section':
            window.location.href = 'http://127.0.0.1:8000/adminpanel/books/';
            break;
        case 'Log out':
            // Signal logout across tabs using localStorage
            localStorage.setItem('logout-event', 'logout' + Date.now());
            window.location.href = "http://127.0.0.1:8000/adminpanel/logout/"; // Redirect to logout view
            break;
        default:
            console.error('Unknown option:', option);
            break;
    }
}   

