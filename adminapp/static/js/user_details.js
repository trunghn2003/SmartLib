
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
    }, 200);  
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


function toggleSelectUser() {
    const selectColumn = document.getElementById('selectColumn');
    const checkboxes = document.querySelectorAll('.select-checkbox');
    const deleteButton = document.getElementById('delete-btn');

    if (!selectColumn || !deleteButton) {
        console.error("Required elements (selectColumn, delete-btn) are missing from the DOM.");
        return;
    }

    const isHidden = selectColumn.style.display === 'none' || selectColumn.style.display === '';
    selectColumn.style.display = isHidden ? 'table-cell' : 'none';

    checkboxes.forEach(checkbox => {
        checkbox.style.display = isHidden ? 'table-cell' : 'none';
        const input = checkbox.querySelector('input');
        if (input) input.checked = false; // Uncheck all checkboxes
    });

    deleteButton.style.display = isHidden ? 'inline-block' : 'none';
}

function deleteSelectedReaders() {
    // Select all checked checkboxes
    const selectedCheckboxes = document.querySelectorAll('.reader-select:checked');
    console.log("Selected checkboxes:", selectedCheckboxes); // Log selected checkboxes

    // Extract IDs from selected checkboxes
    const selectedIds = Array.from(selectedCheckboxes).map(checkbox => checkbox.getAttribute('data-id'));
    console.log("Selected IDs:", selectedIds); // Log selected IDs

    if (selectedIds.length === 0) {
        return;
    }

    if (!confirm('Are you sure you want to deactivate the selected users?')) return;

    // Send requests to deactivate selected users
    const promises = selectedIds.map(userId =>
        fetch(`/adminpanel/deactivate-readers/${userId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
            .then(response => {
                if (!response.ok) throw new Error(`Failed to deactivate user with ID: ${userId}`);
                return response.json();
            })
    );

    Promise.all(promises)
        .then(results => {
            const errors = results.filter(result => result.status !== 'success');
            if (errors.length === 0) {
                window.location.reload();
            } else {
            }
        })
        .catch(error => {
            console.error("Error deactivating readers:", error);
        });
}




function searchUser() {
    const searchInput = document.getElementById("searchInput").value.trim();
    if (searchInput === "") {
        return;
    }

    fetch(`/search-users/?query=${encodeURIComponent(searchInput)}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Indicate AJAX request
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch search results");
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
                const userTableBody = document.getElementById("userTableBody");
                userTableBody.innerHTML = ""; // Clear existing table rows

                if (data.users.length > 0) {
                    data.users.forEach(user => {
                        const newRow = document.createElement("tr");
                        newRow.innerHTML = `
                            <td><input type="checkbox" class="user-select" data-id="${user.user_id}"></td>
                            <td contenteditable="true" class="editable" data-field="user_name">${user.user_name}</td>
                            <td contenteditable="true" class="editable" data-field="email">${user.email}</td>
                            <td>${user.last_login}</td>
                            <td contenteditable="true" class="editable" data-field="is_active">${user.is_active ? "Active" : "Inactive"}</td>
                        `;
                        userTableBody.appendChild(newRow);
                    });
                    enableEditableCells();
                } else {
                    userTableBody.innerHTML = '<tr><td colspan="5">No users found.</td></tr>';
                }
            } else {
            }
        })
        .catch(error => {
            console.error("Error during search:", error);
        });
}




function enableEditableCells() {
    const editableCells = document.querySelectorAll('.editable');

    editableCells.forEach(cell => {
        // Handle cell focus when clicked
        cell.addEventListener('click', function () {
            cell.contentEditable = true; // Enable editing
            cell.focus(); // Focus the cell
            console.log("Cell opened for editing:", cell);
        });

        // Handle Enter key to save and prevent new lines
        cell.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent adding a new line
                console.log("Enter key pressed");

                const row = cell.closest('tr');
                const readerId = row.dataset.id;
                const field = cell.getAttribute('data-field');
                const newValue = cell.textContent.trim();

                if (!readerId || !field) {
                    console.error("Missing data-id or data-field for editable cell");
                    return;
                }

                const confirmUpdate = confirm("Are you sure you want to update this value?");
                if (confirmUpdate) {
                    // Format value for is_active
                    let formattedValue = newValue;
                    if (field === 'is_active') {
                        const valueLower = newValue.toLowerCase();
                        formattedValue = (valueLower === 'active') ? true : false;
                        if (valueLower !== 'active' && valueLower !== 'inactive') {
                            formattedValue = false;
                        }
                    } else if (field === 'reader_point') {
                        formattedValue = parseInt(newValue, 10);
                    }

                    console.log(`Confirmed update. Reader ID: ${readerId}, Field: ${field}, Value: ${formattedValue}`);

                    // Send update request
                    sendUpdateRequest(readerId, field, formattedValue)
                        .then(data => {
                            if (data.status === 'success') {
                                cell.blur(); // Blur to indicate update completed
                            } else {
                                window.location.reload(); // Reload on failure
                            }
                        })
                        .catch(error => {
                            console.error("Error updating cell:", error);
                            window.location.reload();
                        });
                } else {
                    console.log("Update canceled.");
                    window.location.reload(); // Reload to restore original value
                }
            }
        });

        // Blur the cell after editing
        cell.addEventListener('blur', function () {
            cell.contentEditable = false; // Disable editing
            console.log("Cell closed for editing");
        });
    });
}

function sendUpdateRequest(readerId, field, value) {
    console.log(`Sending update request: Reader ID: ${readerId}, Field: ${field}, Value: ${value}`);
    return fetch('/adminpanel/update-reader/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            reader_id: readerId,
            field: field,
            value: value,
        }),
    }).then(response => response.json());
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

// Call the function to enable editable cells
document.addEventListener("DOMContentLoaded", function () {
    enableEditableCells();
});
function enableRankSelects() {
    const rankSelects = document.querySelectorAll('.rank-select');

    rankSelects.forEach(select => {
        select.addEventListener('change', function () {
            const row = select.closest('tr');
            const readerId = row.dataset.id;
            const newValue = select.value; // Selected rank value

            if (!readerId) {
                console.error("Missing data-id for rank dropdown");
                return;
            }

            const confirmUpdate = confirm("Are you sure you want to update the rank?");
            if (confirmUpdate) {
                console.log(`Confirmed rank update. Reader ID: ${readerId}, Rank: ${newValue}`);

                sendUpdateRequest(readerId, 'reader_rank', newValue)
                    .then(data => {
                        if (data.status === 'success') {
                        } else {
                            console.error('Server Error:', data.message);
                        }
                    })
                    .catch(error => {
                        console.error("Error updating rank:", error);
                    });
            } else {
                console.log("Rank update canceled.");
            }
        });
    });
}

// Call this function after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    enableRankSelects();
});


function openInsertForm() {
    const stackPage = document.getElementById('insertStackPage');
    if (stackPage) {
        stackPage.style.display = 'block'; // Show the stack page
    } else {
        console.error('Insert stack page element not found.');
    }
}

function closeInsertForm() {
    const stackPage = document.getElementById('insertStackPage');
    if (stackPage) {
        stackPage.style.display = 'none'; // Hide the stack page
    } else {
        console.error('Insert stack page element not found.');
    }
}



document.addEventListener("DOMContentLoaded", function () {
    const insertUserForm = document.getElementById("insertUserForm");

    // Handle form submission
    insertUserForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(insertUserForm); // Collect form data

        // Extract form data into an object
        const data = {
            user_name: formData.get("user_name"),
            email: formData.get("email"),
            password: formData.get("password"),
            reader_rank: formData.get("reader_rank") || "Rookie", // Default rank
            reader_points: parseInt(formData.get("reader_points"), 10) || 0, // Default points
        };

        // Validate required fields
        if (!data.user_name || !data.email || !data.password) {
            return;
        }

        // Send POST request to add user
        fetch("/adminpanel/add-user/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(data),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to add user");
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "success") {
                    closeInsertForm();
                    window.location.reload();
                } else {
                    if (data.message === "Email already exists in the database.") {
                    } else {
                    }
                }
            })
            .catch(error => {
                console.error("Error adding user:", error);
            });
    });
});


// Utility function to get CSRF token
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

// Utility function to close the insert form
function closeInsertForm() {
    const stackPage = document.getElementById("insertStackPage");
    if (stackPage) {
        stackPage.style.display = "none";
    }
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

