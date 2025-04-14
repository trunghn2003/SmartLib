//-- get categories
// Initialize categoriesList as a hash map
const categoriesList = {};

// Fetch categories and dynamically update the UI
const categoriesContainer = document.getElementById('dropdown-categories'); // Ensure this element exists in your HTML

fetch('/getAllCategories/') // Replace with your actual endpoint
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        return response.json(); // Parse the JSON response
    })
    .then(categories => {
        // Clear existing content in categoriesContainer
        categoriesContainer.innerHTML = '';

        // Store categories as a hash map and update the UI
        categories.forEach(category => {
            // Populate the hash map
            categoriesList[category.category_id] = category.category_name;

            // Dynamically create and append list items
            const listItem = document.createElement('li');
            listItem.textContent = category.category_name; // Display the category name
            listItem.onclick = () => handleOptionClick_categories(category.category_id);
            categoriesContainer.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error('Error fetching categories:', error);
    });

const categoriesButton = document.getElementById('Categories');
const dropdownCategories = document.getElementById('dropdown-categories');
let closeTimeout_categories; // Declare this variable at the start to handle the timeout properly

// Function to show the dropdown
function showDropdown_categories() {
    clearTimeout(closeTimeout_categories); // Cancel any scheduled closing
    dropdownCategories.style.display = 'block';
    categoriesButton.classList.add('active'); // Add 'active' class to keep the hover color
}

// Function to hide the dropdown with a delay
function hideDropdown_categories() {
    closeTimeout_categories = setTimeout(() => {
        dropdownCategories.style.display = 'none';
        categoriesButton.classList.remove('active'); // Remove 'active' class when hidden
    }, 100); // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
categoriesButton.addEventListener('mouseenter', () => {
    showDropdown_categories();
});

// Event listener for when mouse leaves the categories button
categoriesButton.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdownCategories.contains(event.relatedTarget)) {
        hideDropdown_categories();
    }
});

// Event listener for when mouse enters the dropdown
dropdownCategories.addEventListener('mouseenter', () => {
    showDropdown_categories();
});

// Event listener for when mouse leaves the dropdown
dropdownCategories.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!categoriesButton.contains(event.relatedTarget)) {
        hideDropdown_categories();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_categories(category_id) {
    dropdownCategories.style.display = 'none'; // Hide dropdown after selection
    categoriesButton.classList.remove('active'); // Remove 'active' class after selection

    localStorage.setItem('selected_category', category_id);
    window.location.href = '/guest-search-page/?search=';
}


//-----------------------------------------------------
// search:

document.getElementById('search-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') { // Check if the pressed key is 'Enter'
        const inputValue = this.value.trim(); // Get the input value and trim whitespace
        if (inputValue != '') {
            const search_input = encodeURIComponent(inputValue);
            const redirectUrl = `/guest-search-page?search=${search_input}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
        } 

    }
});








//-----------------------------------------------------
// functionality for most readed book

let currentData_most_readed = null; 

document.addEventListener('DOMContentLoaded', () => {
    const book_most_readed_prev = document.getElementById('book_most_readed_prev');
    const book_most_readed_next = document.getElementById('book_most_readed_next');

    const book_most_readed_1 = document.getElementById('book_most_readed_item_1');
    const book_most_readed_2 = document.getElementById('book_most_readed_item_2');
    const book_most_readed_3 = document.getElementById('book_most_readed_item_3');
    const book_most_readed_4 = document.getElementById('book_most_readed_item_4');
    const book_most_readed_5 = document.getElementById('book_most_readed_item_5');

    // Initially hide all book items
    book_most_readed_1.style.display = 'none';
    book_most_readed_2.style.display = 'none';
    book_most_readed_3.style.display = 'none';
    book_most_readed_4.style.display = 'none';
    book_most_readed_5.style.display = 'none';

    // List of book elements
    const booksMostReaded = [
        document.getElementById('book_most_readed_item_1'),
        document.getElementById('book_most_readed_item_2'),
        document.getElementById('book_most_readed_item_3'),
        document.getElementById('book_most_readed_item_4'),
        document.getElementById('book_most_readed_item_5')
    ];

    // Add click event listeners to each book element
    booksMostReaded.forEach((bookElement, index) => {
        if (bookElement) { // Ensure the element exists
            bookElement.addEventListener('click', () => {
                window.location.href = `/login`; // Example URL
            });
        }
    });


    // Fetch initial data when page loads
    fetch(`/getMostReadedBook`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch most readed reading books');
            }
            return response.json();
        })
        .then(data => {
            currentData_most_readed = data; // Store the fetched data
            updateBookDetails_most_readed(data); // Update the book details initially

            // Event listener for "Previous" button
            book_most_readed_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("prev: "+currentData_most_readed.previous);
                if (currentData_most_readed.previous) {
                    loadBooks_most_readed(currentData_most_readed.previous); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_most_readed_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_most_readed.next);
                if (currentData_most_readed.next) {
                    loadBooks_most_readed(currentData_most_readed.next); // Load books for the next page
                }
            });
        })
        .catch(error => {
            console.error('Error fetching continue reading books:', error);
        });
});

// Function to load books based on the next or previous URL
function loadBooks_most_readed(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load books');
            }
            return response.json();
        })
        .then(data => {
            currentData_most_readed = data; // Update the current data
            updateBookDetails_most_readed(data); // Update the book details
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

// Function to update book details and pagination buttons
function updateBookDetails_most_readed(data) {
    const book_most_readed_prev = document.getElementById('book_most_readed_prev');
    const book_most_readed_next = document.getElementById('book_most_readed_next');

    const book_most_readed_1 = document.getElementById('book_most_readed_item_1');
    const book_most_readed_2 = document.getElementById('book_most_readed_item_2');
    const book_most_readed_3 = document.getElementById('book_most_readed_item_3');
    const book_most_readed_4 = document.getElementById('book_most_readed_item_4');
    const book_most_readed_5 = document.getElementById('book_most_readed_item_5');

    // Hide all book items
    book_most_readed_1.style.display = 'none';
    book_most_readed_2.style.display = 'none';
    book_most_readed_3.style.display = 'none';
    book_most_readed_4.style.display = 'none';
    book_most_readed_5.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_most_readed_prev.style.display = 'none';
        book_most_readed_next.style.display = 'none';
    } else if (data.previous == null && data.next != null) {
        book_most_readed_prev.style.display = 'none';
        book_most_readed_next.style.display = 'block';
    } else if (data.previous != null && data.next == null) {
        book_most_readed_prev.style.display = 'block';
        book_most_readed_next.style.display = 'none';
    } else {
        book_most_readed_prev.style.display = 'block';
        book_most_readed_next.style.display = 'block';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`book_most_readed_name_${index + 1}`);
        const bookAuthor = document.getElementById(`book_most_readed_author_${index + 1}`);
        const bookCategory = document.getElementById(`book_most_readed_category_${index + 1}`);
        const bookRating = document.getElementById(`book_most_readed_rating_${index + 1}`);
        const bookImage = document.getElementById(`book_most_readed_image_${index + 1}`);
        const bookItem = document.getElementById(`book_most_readed_item_${index + 1}`);

        // If there is data for the book, display the book item
        if (book) {
            bookItem.style.display = 'block'; // Make the book item visible

            // Update book details
            bookName.textContent = book.book_name || 'No Name';
            bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
            bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
            bookRating.textContent = `Rating: ${'⭐'.repeat(book.book_rating_avg || 0)}`;

            // Update the image (if available)
            if (book.book_image) {
                bookImage.src = book.book_image;
            }
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}

//-----------------------------------------------------

// functionality for most rating book

let currentData_most_rating = null; 

document.addEventListener('DOMContentLoaded', () => {
    const book_most_rating_prev = document.getElementById('book_most_rating_prev');
    const book_most_rating_next = document.getElementById('book_most_rating_next');

    const book_most_rating_1 = document.getElementById('book_most_rating_item_1');
    const book_most_rating_2 = document.getElementById('book_most_rating_item_2');
    const book_most_rating_3 = document.getElementById('book_most_rating_item_3');
    const book_most_rating_4 = document.getElementById('book_most_rating_item_4');
    const book_most_rating_5 = document.getElementById('book_most_rating_item_5');

    // Initially hide all book items
    book_most_rating_1.style.display = 'none';
    book_most_rating_2.style.display = 'none';
    book_most_rating_3.style.display = 'none';
    book_most_rating_4.style.display = 'none';
    book_most_rating_5.style.display = 'none';

    // List of book elements
    const booksMostRating = [
        document.getElementById('book_most_rating_item_1'),
        document.getElementById('book_most_rating_item_2'),
        document.getElementById('book_most_rating_item_3'),
        document.getElementById('book_most_rating_item_4'),
        document.getElementById('book_most_rating_item_5')
    ];

    // Add click event listeners to each book element
    booksMostRating.forEach((bookElement, index) => {
        if (bookElement) { // Ensure the element exists
            bookElement.addEventListener('click', () => {
                window.location.href = `/login`; // Example URL
            });
        }
    });


    // Fetch initial data when page loads
    fetch(`/getMostRatingBook`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch most rated books');
            }
            return response.json();
        })
        .then(data => {
            currentData_most_rating = data; // Store the fetched data
            updateBookDetails_most_rating(data); // Update the book details initially

            // Event listener for "Previous" button
            book_most_rating_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("prev: "+currentData_most_rating.previous);
                if (currentData_most_rating.previous) {
                    loadBooks_most_rating(currentData_most_rating.previous); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_most_rating_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_most_rating.next);
                if (currentData_most_rating.next) {
                    loadBooks_most_rating(currentData_most_rating.next); // Load books for the next page
                }
            });
        })
        .catch(error => {
            console.error('Error fetching most rated books:', error);
        });
});

// Function to load books based on the next or previous URL
function loadBooks_most_rating(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load books');
            }
            return response.json();
        })
        .then(data => {
            currentData_most_rating = data; // Update the current data
            updateBookDetails_most_rating(data); // Update the book details
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

// Function to update book details and pagination buttons
function updateBookDetails_most_rating(data) {
    const book_most_rating_prev = document.getElementById('book_most_rating_prev');
    const book_most_rating_next = document.getElementById('book_most_rating_next');

    const book_most_rating_1 = document.getElementById('book_most_rating_item_1');
    const book_most_rating_2 = document.getElementById('book_most_rating_item_2');
    const book_most_rating_3 = document.getElementById('book_most_rating_item_3');
    const book_most_rating_4 = document.getElementById('book_most_rating_item_4');
    const book_most_rating_5 = document.getElementById('book_most_rating_item_5');

    // Hide all book items
    book_most_rating_1.style.display = 'none';
    book_most_rating_2.style.display = 'none';
    book_most_rating_3.style.display = 'none';
    book_most_rating_4.style.display = 'none';
    book_most_rating_5.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_most_rating_prev.style.display = 'none';
        book_most_rating_next.style.display = 'none';
    } else if (data.previous == null && data.next != null) {
        book_most_rating_prev.style.display = 'none';
        book_most_rating_next.style.display = 'block';
    } else if (data.previous != null && data.next == null) {
        book_most_rating_prev.style.display = 'block';
        book_most_rating_next.style.display = 'none';
    } else {
        book_most_rating_prev.style.display = 'block';
        book_most_rating_next.style.display = 'block';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`book_most_rating_name_${index + 1}`);
        const bookAuthor = document.getElementById(`book_most_rating_author_${index + 1}`);
        const bookCategory = document.getElementById(`book_most_rating_category_${index + 1}`);
        const bookRating = document.getElementById(`book_most_rating_rating_${index + 1}`);
        const bookImage = document.getElementById(`book_most_rating_image_${index + 1}`);
        const bookItem = document.getElementById(`book_most_rating_item_${index + 1}`);

        // If there is data for the book, display the book item
        if (book) {
            bookItem.style.display = 'block'; // Make the book item visible

            // Update book details
            bookName.textContent = book.book_name || 'No Name';
            bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
            bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
            bookRating.textContent = `Rating: ${'⭐'.repeat(book.book_rating_avg || 0)}`;

            // Update the image (if available)
            if (book.book_image) {
                bookImage.src = book.book_image;
            }
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}


//-----------------------------------------------------

// functionality for last updated book

let currentData_last_updated = null; 

document.addEventListener('DOMContentLoaded', () => {
    const book_last_updated_prev = document.getElementById('book_last_updated_prev');
    const book_last_updated_next = document.getElementById('book_last_updated_next');

    const book_last_updated_1 = document.getElementById('book_last_updated_item_1');
    const book_last_updated_2 = document.getElementById('book_last_updated_item_2');
    const book_last_updated_3 = document.getElementById('book_last_updated_item_3');
    const book_last_updated_4 = document.getElementById('book_last_updated_item_4');
    const book_last_updated_5 = document.getElementById('book_last_updated_item_5');

    // Initially hide all book items
    book_last_updated_1.style.display = 'none';
    book_last_updated_2.style.display = 'none';
    book_last_updated_3.style.display = 'none';
    book_last_updated_4.style.display = 'none';
    book_last_updated_5.style.display = 'none';

    // List of book elements
    const booksLastUpdated = [
        document.getElementById('book_last_updated_item_1'),
        document.getElementById('book_last_updated_item_2'),
        document.getElementById('book_last_updated_item_3'),
        document.getElementById('book_last_updated_item_4'),
        document.getElementById('book_last_updated_item_5')
    ];

    // Add click event listeners to each book element
    booksLastUpdated.forEach((bookElement, index) => {
        if (bookElement) { // Ensure the element exists
            bookElement.addEventListener('click', () => {
                window.location.href = '/login'; // Example URL
            });
        }
    });


    // Fetch initial data when page loads
    fetch(`/getLastUploadedBook`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch last updated books');
            }
            return response.json();
        })
        .then(data => {
            currentData_last_updated = data; // Store the fetched data
            updateBookDetails_last_updated(data); // Update the book details initially

            // Event listener for "Previous" button
            book_last_updated_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("prev: "+currentData_last_updated.previous);
                if (currentData_last_updated.previous) {
                    loadBooks_last_updated(currentData_last_updated.previous); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_last_updated_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_last_updated.next);
                if (currentData_last_updated.next) {
                    loadBooks_last_updated(currentData_last_updated.next); // Load books for the next page
                }
            });
        })
        .catch(error => {
            console.error('Error fetching last updated books:', error);
        });
});

// Function to load books based on the next or previous URL
function loadBooks_last_updated(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load books');
            }
            return response.json();
        })
        .then(data => {
            currentData_last_updated = data; // Update the current data
            updateBookDetails_last_updated(data); // Update the book details
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

// Function to update book details and pagination buttons
function updateBookDetails_last_updated(data) {
    const book_last_updated_prev = document.getElementById('book_last_updated_prev');
    const book_last_updated_next = document.getElementById('book_last_updated_next');

    const book_last_updated_1 = document.getElementById('book_last_updated_item_1');
    const book_last_updated_2 = document.getElementById('book_last_updated_item_2');
    const book_last_updated_3 = document.getElementById('book_last_updated_item_3');
    const book_last_updated_4 = document.getElementById('book_last_updated_item_4');
    const book_last_updated_5 = document.getElementById('book_last_updated_item_5');

    // Hide all book items
    book_last_updated_1.style.display = 'none';
    book_last_updated_2.style.display = 'none';
    book_last_updated_3.style.display = 'none';
    book_last_updated_4.style.display = 'none';
    book_last_updated_5.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_last_updated_prev.style.display = 'none';
        book_last_updated_next.style.display = 'none';
    } else if (data.previous == null && data.next != null) {
        book_last_updated_prev.style.display = 'none';
        book_last_updated_next.style.display = 'block';
    } else if (data.previous != null && data.next == null) {
        book_last_updated_prev.style.display = 'block';
        book_last_updated_next.style.display = 'none';
    } else {
        book_last_updated_prev.style.display = 'block';
        book_last_updated_next.style.display = 'block';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`book_last_updated_name_${index + 1}`);
        const bookAuthor = document.getElementById(`book_last_updated_author_${index + 1}`);
        const bookCategory = document.getElementById(`book_last_updated_category_${index + 1}`);
        const bookRating = document.getElementById(`book_last_updated_rating_${index + 1}`);
        const bookImage = document.getElementById(`book_last_updated_image_${index + 1}`);
        const bookItem = document.getElementById(`book_last_updated_item_${index + 1}`);

        // If there is data for the book, display the book item
        if (book) {
            bookItem.style.display = 'block'; // Make the book item visible

            // Update book details
            bookName.textContent = book.book_name || 'No Name';
            bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
            bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
            bookRating.textContent = `Rating: ${'⭐'.repeat(book.book_rating_avg || 0)}`;

            // Update the image (if available)
            if (book.book_image) {
                bookImage.src = book.book_image;
            }
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}
