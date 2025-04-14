
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
//------------------------------------
let currentBookPage = 1;
let categories = []; 


let currentPage = 1; // Define globally
let totalPages = 1; // Total pages

function fetchBooks(page = 1) {
    if (page < 1 || page > totalPages) return; // Prevent invalid page navigation

    Promise.all([
        fetch(`/adminpanel/api/books/?page=${page}&limit=4`).then(res => res.json()), // Fetch books
        fetch(`/adminpanel/api/categories/`).then(res => res.json()) // Fetch categories
    ])
    .then(([booksData, categoriesData]) => {
        const books = booksData.books || [];
        const categories = categoriesData.categories || [];
        const tbody = document.getElementById('book-table-body');
        tbody.innerHTML = ''; 

        totalPages = booksData.total_pages || 1; // Update total pages
        currentPage = booksData.current_page; // Update current page

        if (books.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">No books available.</td></tr>';
            return;
        }

        // Populate the table with books
        books.forEach(book => {
            const row = document.createElement('tr');
            row.setAttribute('data-book-id', book.book_id);

            // Create the category dropdown
            let categoryDropdown = `<select data-id="${book.book_id}" data-field="category_name" onchange="saveBookField(this)">`;
            categories.forEach(category => {
                const isSelected = category.category_name === book.category_name ? 'selected' : '';
                categoryDropdown += `<option value="${category.category_name}" ${isSelected}>${category.category_name}</option>`;
            });
            categoryDropdown += `</select>`;

            // Populate the row
            row.innerHTML = `
                <td data-field="book_name" contenteditable="true" class="scrollable-cell">${book.book_name || 'N/A'}</td>
                <td data-field="book_author" contenteditable="true" class="scrollable-cell">${book.book_author || 'Unknown'}</td>
                <td data-field="book_barcode" contenteditable="true" class="scrollable-cell">${book.book_barcode || 'N/A'}</td>
                <td class="scrollable-cell">
                    <img src="${book.book_image || '/static/images/default.png'}" alt="Book Cover" width="50">
                </td>
                <td class="scrollable-cell">${categoryDropdown}</td>
                <td class="scrollable-cell">
                    <select data-id="${book.book_id}" data-field="status" onchange="saveBookField(this)">
                        <option value="Pending" ${book.status === 'Pending' ? 'selected' : ''}>Pending</option>
                        <option value="Accepted" ${book.status === 'Accepted' ? 'selected' : ''}>Accepted</option>
                        <option value="Rejected" ${book.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                    </select>
                </td>
                <td data-field="book_description" contenteditable="true" class="scrollable-cell">${book.book_description || 'No Description'}</td>
            `;

            tbody.appendChild(row);
        });

        enableCellEditing(); // Enable cell editing for the table
        updatePagination(totalPages, currentPage); // Update pagination UI
    })
    .catch(error => {
        console.error('Error fetching books or categories:', error);
    });
}

function updatePagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageNumbers = document.getElementById('pageNumbers');

    // Clear page numbers
    pageNumbers.innerHTML = '';

    // Update button states
    prevButton.disabled = currentPage <= 1;
    nextButton.disabled = currentPage >= totalPages;

    // Generate page numbers
    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.innerText = i;
        pageButton.className = i === currentPage ? 'current-page' : '';
        pageButton.addEventListener('click', () => fetchBooks(i));
        pageNumbers.appendChild(pageButton);
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


function saveBookField(selectElement) {
    const newValue = selectElement.value; 
    const bookId = selectElement.getAttribute('data-id'); 
    const field = selectElement.getAttribute('data-field'); 

    console.log('Updating book field:', { bookId, field, newValue }); 

    fetch(`/adminpanel/api/books/${bookId}/`, { 
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            [field]: newValue,
        }),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to update book. Status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (data.status === 'success') {
            } else {
            }
        })
        .catch((error) => {
            console.error('Error updating book field:', error);
        });
}

function enableCellEditing() {
    const tableBody = document.getElementById('book-table-body');
    tableBody.addEventListener('blur', (event) => {
        const target = event.target;
        const field = target.getAttribute('data-field');

        if (target.isContentEditable) {
            const newValue = target.textContent.trim();
            const bookId = target.closest('tr').getAttribute('data-book-id');

            if (newValue) {
                updateBook(bookId, field, newValue);
            }
        }
    }, true);
}

function updateBook(bookId, field, value) {
    console.log(`Updating book: ID=${bookId}, Field=${field}, Value=${value}`);

    return fetch(`/adminpanel/api/books/${bookId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ [field]: value }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to update book. Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Book updated successfully:', data);
        })
        .catch(error => {
            console.error('Error updating book:', error);
        });
}
document.addEventListener('DOMContentLoaded', () => {
    fetchBooks(currentBookPage); 
});

function toggleSelectBooks() {
    const deleteButton = document.getElementById('delete-btn-books');
    const tableHead = document.querySelector('.content-table-book thead tr');
    const tableBody = document.querySelector('.content-table-book tbody');
    const rows = tableBody.querySelectorAll('tr');

    if (!tableHead) {
        console.error("Table header not found.");
        return;
    }

    const isSelectionEnabled = tableHead.querySelector('.book-select-column');

    if (!isSelectionEnabled) {
        // Add "Select" column header
        const selectHeader = document.createElement('th');
        selectHeader.classList.add('book-select-column');
        selectHeader.textContent = 'Select';
        tableHead.prepend(selectHeader);

        // Add checkboxes to each row
        rows.forEach(row => {
            if (!row.querySelector('.book-select-checkbox')) {
                const checkboxCell = document.createElement('td');
                checkboxCell.innerHTML = '<input type="checkbox" class="book-select-checkbox">';
                row.prepend(checkboxCell);
            }
        });

        // Show the delete button
        deleteButton.style.display = 'inline-block';
    } else {
        // Remove "Select" column header
        const selectHeader = tableHead.querySelector('.book-select-column');
        if (selectHeader) {
            selectHeader.remove();
        }

        // Remove checkboxes from each row
        rows.forEach(row => {
            const checkboxCell = row.querySelector('.book-select-checkbox');
            if (checkboxCell) {
                checkboxCell.closest('td').remove();
            }
        });

        // Hide the delete button
        deleteButton.style.display = 'none';
    }
}

function deleteSelectedBooks() {
    const selectedCheckboxes = document.querySelectorAll('.book-select-checkbox:checked');
    const selectedBookIds = Array.from(selectedCheckboxes).map(checkbox => {
        return checkbox.closest('tr').getAttribute('data-book-id');
    });

    // Check if no books are selected
    if (selectedBookIds.length === 0) {
        return;
    }

    // Confirm deletion action
    if (!confirm('Are you sure you want to delete the selected books?')) {
        return;
    }

    // Track the results of deletion for each book
    const deletePromises = selectedBookIds.map(bookId =>
        fetch(`/adminpanel/api/books/${bookId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), // Add CSRF token for security
                'Content-Type': 'application/json' // Ensure the correct content type
            }
        })
            .then(response => {
                if (!response.ok) {
                    // Throw an error if the request fails
                    throw new Error(`Failed to delete book with ID ${bookId}. Status: ${response.status}`);
                }
                return response.json();
            })
    );

    // Execute all delete requests and handle the results
    Promise.allSettled(deletePromises)
        .then(results => {
            // Process results to determine success and failures
            const failedDeletions = results
                .filter(result => result.status === 'rejected') // Filter for failed requests
                .map((_, index) => selectedBookIds[index]); // Map back to failed book IDs

            if (failedDeletions.length > 0) {
                console.error('Failed deletions:', failedDeletions);
            } else {
            }

            // Refresh the current page after deletion
            window.location.reload(); // Refresh the current page
        })
        .catch(error => {
            console.error('Error during deletion process:', error);
        });
}



function openUploadForm() {
    document.getElementById("upload-book-container").style.display = "flex";
}

function closeUploadForm() {
    document.getElementById("upload-book-container").style.display = "none";
}








document.addEventListener("DOMContentLoaded", function () {
    fetchCategories();
});

function fetchCategories() {
    console.log("Fetching categories..."); // Debugging
    fetch("/adminpanel/api/categories/")
        .then(response => {
            console.log("Fetch response status:", response.status); // Debugging
            return response.json();
        })
        .then(data => {
            console.log("Categories data:", data); // Debugging
            const categorySelect = document.getElementById("category");
            categorySelect.innerHTML = '<option value="" disabled selected>Select Category</option>';
            data.categories.forEach(category => {
                const option = document.createElement("option");
                option.value = category.category_id;
                option.textContent = category.category_name;
                categorySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error fetching categories:", error);
        });
}

document.addEventListener("DOMContentLoaded", fetchCategories);



document.addEventListener("DOMContentLoaded", function () {
    fetchCategories();
});

function submitForm(event) {
    event.preventDefault(); 

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    fetch("/adminpanel/api/books/add", {
        method: "POST",
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
            } else {
            }
        })
        .catch(error => console.error("Error submitting form:", error));
    
}

function searchBooks() {
    // Get the search input value
    const searchInput = document.getElementById('searchInputbook').value.toLowerCase().trim();

    // Get the table body containing the rows of books
    const tableBody = document.getElementById('book-table-body');

    // Get all rows in the table body
    const rows = tableBody.getElementsByTagName('tr');

    // Check if there are rows in the table
    let noMatchFound = true;

    // Loop through each row and check if the book name or status matches the search query
    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];

        // Get the cells for book name and status
        const bookNameCell = row.getElementsByTagName('td')[0]; // First column: Book Name
        const bookStatusCell = row.getElementsByTagName('td')[5]; // Sixth column: Status

        // Check if the book name or status matches the search query
        const matchesName = bookNameCell && bookNameCell.textContent.toLowerCase().includes(searchInput);
        const matchesStatus = bookStatusCell && bookStatusCell.textContent.toLowerCase().includes(searchInput);

        if (matchesName || matchesStatus) {
            row.style.display = ''; // Show the row if it matches
            noMatchFound = false;
        } else {
            row.style.display = 'none'; // Hide the row if it doesn't match
        }
    }

    // If no match is found, display a message
    const noResultsRow = document.getElementById('no-results-row');
    if (noMatchFound) {
        if (!noResultsRow) {
            const newRow = document.createElement('tr');
            newRow.id = 'no-results-row';
            newRow.innerHTML = '<td colspan="7">No matching books found.</td>';
            tableBody.appendChild(newRow);
        }
    } else {
        if (noResultsRow) {
            noResultsRow.remove();
        }
    }
}


// Add an event listener to trigger search when pressing Enter
const searchInputField = document.getElementById('searchInputbook');
searchInputField.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        searchBooks();
    }
});
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


//-------------------
// Function to open the file input when the drag-and-drop area is clicked
function triggerFileInput() {
    document.getElementById('fileInput').click();
}

// Function to handle file selection
function fileSelected(event) {
    const file = event.target.files[0];
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeLabel = document.getElementById('fileSizeLabel');

    if (file) {
        fileNameDisplay.textContent = file.name;
        fileSizeLabel.textContent = `Size: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    } else {
        fileNameDisplay.textContent = '';
        fileSizeLabel.textContent = 'No file selected';
    }
}

// Function to trigger image input for book cover
function triggerImageInput(imageInputId) {
    document.getElementById(imageInputId).click();
}

// Function to preview the selected image
function previewImage(event, imagePreviewId) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById(imagePreviewId);

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Function to handle form submission
async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);

    try {
        const response = await fetch('/adminpanel/api/books/add', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            return;
        }

        const result = await response.json();
        if (result.status === 'success') {
            // Redirect to /adminpanel/books
            window.location.href = '/adminpanel/books';
        } else {
        }
    } catch (error) {
        console.error('Error occurred:', error);
    }
}

// Function to close the upload modal
function closeUploadForm() {
    const uploadContainer = document.getElementById('upload-book-container');
    uploadContainer.style.display = 'none';

    // Reset the form
    document.getElementById('uploadForm').reset();
    document.getElementById('fileNameDisplay').textContent = '';
    document.getElementById('fileSizeLabel').textContent = 'No file selected';
    document.getElementById('imagePreview1').style.display = 'none';
}
