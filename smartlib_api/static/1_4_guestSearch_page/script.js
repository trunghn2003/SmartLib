const category_id=localStorage.getItem('selected_category');

localStorage.removeItem('selected_category');


fetch('/getAllCategories/')
.then(response => {
    if (!response.ok) {
        throw new Error('Failed to fetch categories');
    }
    return response.json(); // Parse the JSON response
})
.then(categories => {
    // Reference the container where checkboxes will be added
    const categoriesContainer = document.querySelector('.categories_checkBox');

    // Clear existing content in categoriesContainer
    categoriesContainer.innerHTML = '<label>Categories:</label>';

    // Dynamically create checkboxes for each category
    categories.forEach(category => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';

        // Create the checkbox input
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = category.category_id;
        checkbox.name = 'category';
        checkbox.value = category.category_name;

        // Create the label for the checkbox
        const label = document.createElement('label');
        label.htmlFor = category.category_id; // Associate label with the checkbox
        label.textContent = category.category_name;
        label.style.fontWeight = 'normal';
        label.style.fontSize = '15px';
        label.style.marginLeft = '10px';

        // Append checkbox and label to the option div
        optionDiv.appendChild(checkbox);
        optionDiv.appendChild(label);

        // Append the option div to the container
        categoriesContainer.appendChild(optionDiv);

        // Check if the current checkbox id matches the selected category from localStorage
        if (checkbox.id === category_id) {
            checkbox.checked = true;
        }
    });
})
.catch(error => {
    console.error('Error fetching categories:', error);
});









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

        // debug
        // console.log('Categories:', categoriesList);
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
// get url search

document.getElementById('search-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') { // Check if the pressed key is 'Enter'
        const inputValue = this.value.trim(); // Get the input value and trim whitespace
        if (inputValue != '') {
            const search_input = encodeURIComponent(inputValue);
            const redirectUrl = `/guest-search-page?search=${search_input}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
        } 



        document.getElementById('sorting_way').value=='nothing';

        document.querySelectorAll('input[name="category"]').forEach(checkbox => {
            checkbox.checked = false;  // Uncheck all category checkboxes
        });

        star_numbers = 0;
        star_num.textContent = ""; // Reset star_num text
        resetStars(); // Reset star styles to default
        stars.forEach(star => star.classList.remove('active'));


    }
});


const url = window.location.href;
let searchValue = url.split('?search=')[1].split('&')[0]; // Get the value after '?search='
searchValue=decodeURIComponent(searchValue);

document.getElementById('search-input').setAttribute('value', searchValue);

first_url_search=`/search/?search=${searchValue}`;

if(category_id){
    first_url_search += `&category=${category_id}`;
}

let currentData = null; 

document.addEventListener('DOMContentLoaded', () => {
    
    const book_prev = document.getElementById('prev');
    const book_next = document.getElementById('next');

    const book_1 = document.getElementById('card_1');
    const book_2 = document.getElementById('card_2');
    const book_3 = document.getElementById('card_3');
    const book_4 = document.getElementById('card_4');

    // Initially hide all book items
    book_1.style.display = 'none';
    book_2.style.display = 'none';
    book_3.style.display = 'none';
    book_4.style.display = 'none';

    // Fetch initial data when page loads
    fetch(first_url_search)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch books');
            }
            return response.json();
        })
        .then(data => {
            currentData = data; // Store the fetched data
            updateBookDetails(data); // Update the book details initially
            
            if (data.results.length == 3) {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'flex';
                document.getElementById('hr_3').style.display = 'none';
            } else if (data.results.length == 2) {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'none';
                document.getElementById('hr_3').style.display = 'none';
            } else if (data.results.length <= 1) {
                document.getElementById('hr_1').style.display = 'none';
                document.getElementById('hr_2').style.display = 'none';
                document.getElementById('hr_3').style.display = 'none';
            } else {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'flex';
                document.getElementById('hr_3').style.display = 'flex';
            }
            
            // Event listener for "Previous" button
            book_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                if (currentData.previous) {
                    curr_url_continue=currentData.previous;
                    loadBooks(curr_url_continue); 
                }
            });

            // Event listener for "Next" button
            book_next.addEventListener('click', (event) => {
                event.preventDefault(); 
                if (currentData.next) {
                    curr_url_continue=currentData.next;
                    loadBooks(curr_url_continue); 
                }
            });
        })
        .catch(error => {
            console.error('Error fetching books:', error);
        });


// Function to load books based on the next or previous URL
function loadBooks(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load books');
            }
            return response.json();
        })
        .then(data => {
            currentData = data; // Update the current data
            if (data.results.length == 3) {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'flex';
                document.getElementById('hr_3').style.display = 'none';
            } else if (data.results.length == 2) {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'none';
                document.getElementById('hr_3').style.display = 'none';
            } else if (data.results.length <= 1) {
                document.getElementById('hr_1').style.display = 'none';
                document.getElementById('hr_2').style.display = 'none';
                document.getElementById('hr_3').style.display = 'none';
            } else {
                document.getElementById('hr_1').style.display = 'flex';
                document.getElementById('hr_2').style.display = 'flex';
                document.getElementById('hr_3').style.display = 'flex';
            }

            updateBookDetails(data); // Update the book details
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

// Function to update book details and pagination buttons
function updateBookDetails(data) {
    const book_prev = document.querySelector('#prev img');
    const book_next = document.querySelector('#next img');

    const book_1 = document.getElementById('card_1');
    const book_2 = document.getElementById('card_2');
    const book_3 = document.getElementById('card_3');
    const book_4 = document.getElementById('card_4');
    

    // Initially hide all book items
    book_1.style.display = 'none';
    book_2.style.display = 'none';
    book_3.style.display = 'none';
    book_4.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_prev.src = '/static/images/prev_page_empty.png';
        book_next.src = '/static/images/next_page_empty.png';
    } else if (data.previous == null && data.next != null) {
        book_prev.src = '/static/images/prev_page_empty.png';
        book_next.src = '/static/images/next_page.png';
    } else if (data.previous != null && data.next == null) {
        book_prev.src = '/static/images/prev_page.png';
        book_next.src = '/static/images/next_page_empty.png';
    } else {
        book_prev.src = '/static/images/prev_page.png';
        book_next.src = '/static/images/next_page.png';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`title_${index + 1}`);
        const bookAuthor = document.getElementById(`author_${index + 1}`);
        const bookCategory = document.getElementById(`category_${index + 1}`);
        const bookRating = document.getElementById(`rating_${index + 1}`)
        const bookImage = document.getElementById(`book_last_updated_image_${index + 1}`);
        const bookItem = document.getElementById(`card_${index + 1}`);

        bookName.addEventListener('mouseover', () => {
            bookName.style.cursor = "pointer";
            bookName.style.textDecoration = "underline";
        });
        
        bookName.addEventListener('mouseout', () => {
            bookName.style.textDecoration = "none";
        });
        
        // If there is data for the book, display the book item
        if (book) {
            bookItem.style.display = 'flex'; // Make the book item visible

            // Update book details
            bookName.textContent = book.book_name || 'No Name';
            bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
            bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
            bookRating.textContent = `Rating: ${'⭐'.repeat(book.book_rating_avg || 0)}`;
            
            // Update the image (if available)
            if (book.book_image) {
                bookImage.src = book.book_image;
            }

            bookName.addEventListener('click', () => {
                window.location.href = `/login`;
            });
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}
});

//-----------------------------------------------------
// Stars Rating

const stars = document.querySelectorAll('.star');
const star_num = document.getElementById('star_num');
let star_numbers = 0;
let timeout_star_num; // Variable to store the timeout ID

stars.forEach((star, index) => {
    // Hover effect
    star.addEventListener('mouseover', function () {
        clearTimeout(timeout_star_num); // Clear any previous timeout
        resetStars();
        highlightStars(index);
        star_num.textContent = (index + 1) + " Stars"; // Update the text inside <p>
    });

    // Remove hover effect when the mouse leaves
    star.addEventListener('mouseout', function () {
        resetStars();
        const activeStars = document.querySelectorAll('.star.active');
        activeStars.forEach((s, i) => highlightStars(i));

        if (activeStars.length > 0) {
            star_num.textContent = activeStars.length + " Stars"; // Keep the active star count
        } else {
            // Delay the reset by 0.5 seconds
            timeout_star_num = setTimeout(() => {
                star_num.textContent = ""; // Reset to empty after 0.5s
            }, 180);
        }
    });

    // Click event to select the rating
    star.addEventListener('click', function () {
        clearTimeout(timeout_star_num); // Clear any previous timeout
        stars.forEach(s => s.classList.remove('active'));
        highlightStars(index);
        stars.forEach((s, i) => {
            if (i <= index) {
                s.classList.add('active');
            }
        });

        const rating = index + 1; // Index starts from 0, so add 1
        star_num.textContent = rating + " Stars"; // Update the text after selection
        star_numbers = rating;
    });
});

// Helper function to highlight stars
function highlightStars(index) {
    for (let i = 0; i <= index; i++) {
        stars[i].style.color = '#FFD700'; // Golden color for highlighted stars
    }
}

// Helper function to reset stars color
function resetStars() {
    stars.forEach(star => {
        star.style.color = '#ddd'; // Reset to grey
    });
}


//----------------------------------------------------

let filter_url=`/search/?search=${searchValue}`;

document.getElementById('filter').addEventListener('click', (event) => {
    event.preventDefault();
    
    
    // sort way:
    if(document.getElementById('sorting_way').value!='nothing'){
        filter_url+=`&sort_by=${document.getElementById('sorting_way').value}`;
    }


    // sort category:
    const selectedCategories = [];
    const categoryCheckboxes = document.querySelectorAll('input[name="category"]:checked');
    
    // Loop through checked checkboxes and collect their values
    categoryCheckboxes.forEach(checkbox => {
        selectedCategories.push(checkbox.id);  // Push the category value
    });

    // Add the selected categories to the URL, if any
    if (selectedCategories.length > 0) {
        filter_url += `&category=${selectedCategories.join(',')}`;
    }




    // sort rating:
    if(star_numbers!=0){
        filter_url+=`&min_rating=${star_numbers}`;
    }





        const book_prev = document.getElementById('prev');
        const book_next = document.getElementById('next');
    
        const book_1 = document.getElementById('card_1');
        const book_2 = document.getElementById('card_2');
        const book_3 = document.getElementById('card_3');
        const book_4 = document.getElementById('card_4');
    
        // Initially hide all book items
        book_1.style.display = 'none';
        book_2.style.display = 'none';
        book_3.style.display = 'none';
        book_4.style.display = 'none';
    
        // Fetch initial data when page loads
        fetch(filter_url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch books');
                }
                return response.json();
            })
            .then(data => {
                currentData = data; // Store the fetched data
                updateBookDetails(data); // Update the book details initially
                filter_url=`/search/?search=${searchValue}`;
                if (data.results.length == 3) {
                    document.getElementById('hr_1').style.display = 'flex';
                    document.getElementById('hr_2').style.display = 'flex';
                    document.getElementById('hr_3').style.display = 'none';
                } else if (data.results.length == 2) {
                    document.getElementById('hr_1').style.display = 'flex';
                    document.getElementById('hr_2').style.display = 'none';
                    document.getElementById('hr_3').style.display = 'none';
                } else if (data.results.length <= 1) {
                    document.getElementById('hr_1').style.display = 'none';
                    document.getElementById('hr_2').style.display = 'none';
                    document.getElementById('hr_3').style.display = 'none';
                } else {
                    document.getElementById('hr_1').style.display = 'flex';
                    document.getElementById('hr_2').style.display = 'flex';
                    document.getElementById('hr_3').style.display = 'flex';
                }
                
                // Event listener for "Previous" button
                book_prev.addEventListener('click', (event) => {
                    event.preventDefault(); // Prevent the default anchor behavior
                    if (currentData.previous) {
                        curr_url_continue=currentData.previous;
                        loadBooks(curr_url_continue); 
                    }
                });
    
                // Event listener for "Next" button
                book_next.addEventListener('click', (event) => {
                    event.preventDefault(); 
                    if (currentData.next) {
                        curr_url_continue=currentData.next;
                        loadBooks(curr_url_continue); 
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching books:', error);
            });
    
    
    // Function to load books based on the next or previous URL
    function loadBooks(url) {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load books');
                }
                return response.json();
            })
            .then(data => {
                currentData = data; // Update the current data
                updateBookDetails(data); // Update the book details
            })
            .catch(error => {
                console.error('Error loading books:', error);
            });
    }
    
    // Function to update book details and pagination buttons
    function updateBookDetails(data) {
        const book_prev = document.querySelector('#prev img');
        const book_next = document.querySelector('#next img');
    
        const book_1 = document.getElementById('card_1');
        const book_2 = document.getElementById('card_2');
        const book_3 = document.getElementById('card_3');
        const book_4 = document.getElementById('card_4');
        
    
        // Initially hide all book items
        book_1.style.display = 'none';
        book_2.style.display = 'none';
        book_3.style.display = 'none';
        book_4.style.display = 'none';
    
        // Show or hide pagination buttons based on available data
        if (data.previous == null && data.next == null) {
            book_prev.src = '/static/images/prev_page_empty.png';
            book_next.src = '/static/images/next_page_empty.png';
        } else if (data.previous == null && data.next != null) {
            book_prev.src = '/static/images/prev_page_empty.png';
            book_next.src = '/static/images/next_page.png';
        } else if (data.previous != null && data.next == null) {
            book_prev.src = '/static/images/prev_page.png';
            book_next.src = '/static/images/next_page_empty.png';
        } else {
            book_prev.src = '/static/images/prev_page.png';
            book_next.src = '/static/images/next_page.png';
        }
    
        // Update the book details dynamically
        data.results.forEach((book, index) => {
            const bookName = document.getElementById(`title_${index + 1}`);
            const bookAuthor = document.getElementById(`author_${index + 1}`);
            const bookCategory = document.getElementById(`category_${index + 1}`);
            const bookRating = document.getElementById(`rating_${index + 1}`)
            const bookImage = document.getElementById(`book_last_updated_image_${index + 1}`);
            const bookItem = document.getElementById(`card_${index + 1}`);
    
            // If there is data for the book, display the book item
            if (book) {
                bookItem.style.display = 'flex'; // Make the book item visible
    
                // Update book details
                bookName.textContent = book.book_name || 'No Name';
                bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
                bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
                bookRating.textContent = `Rating: ${'⭐'.repeat(book.book_rating_avg || 0)}`;
                
                // Update the image (if available)
                if (book.book_image) {
                    bookImage.src = book.book_image;
                }
    
                bookName.addEventListener('click', () => {
                    window.location.href = `/login`;
                });
            } else {
                // If no data for the book, hide the book item
                bookItem.style.display = 'none';
            }
        });
    }
    
});