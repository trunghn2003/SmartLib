
//-- Auth Access --

let userId = -1;  
let user_name="";
let user_rank="";
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('jwt_token');
    const isDailyLogin = localStorage.getItem('isDailyLogin');


    if (!token) {
        window.location.href = '/login'; // Redirect to login if token is missing
        return;
    }

    try {
        // Decode the JWT token to get the user data
        const decodedToken = jwt_decode(token);
        userId = decodedToken.id; // Extract the user ID

        // Check if the token has expired
        const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
        if (decodedToken.exp < currentTime) {
            // If the token is expired, redirect to login page
            console.error('Token has expired.');
            localStorage.removeItem('jwt_token'); // Remove expired token
            window.location.href = '/login'; // Redirect to login page
            return;
        }
        else {
            // Refresh token before expiration
            const response = await fetch('/refresh-token-api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: token })
            });
    
            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }
    
            const data = await response.json();
            localStorage.setItem('jwt_token', data.jwt);
        }

        console.log('User ID:', userId);

        // Check if user_id is available
        if (userId !== -1) {
            // Make an API call to fetch the user_name using user_id
            fetch(`/get_username/${userId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.user_name) {
                        const user_name = data.user_name;  // Assign the fetched user_name
                        document.getElementById('hello_message').textContent = "Hello, " + user_name;
                        console.log("User Name:", user_name);  // You can use the user_name here
                    } else {
                        console.error("User name not found");
                    }
                })
                .catch(error => {
                    console.error("Error fetching user name:", error);
                });

            fetch(`/get_reader_info?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    const reader_rank = data.reader_rank;  // Assign the fetched reader_rank
                    document.getElementById('user_rank').textContent = "Rank: " + reader_rank;

                    if(reader_rank=="Rookie"){
                        document.getElementById('img_rank').src = '/static/images/rookie_rank.png'; 
                    }
                    else if(reader_rank=="Bronze"){
                        document.getElementById('img_rank').src = '/static/images/bronze_rank.png'; 
                    }
                    else if(reader_rank=="Silver"){
                        document.getElementById('img_rank').src = '/static/images/silver_rank.png'; 
                    }
                    else if(reader_rank=="Gold"){
                        document.getElementById('img_rank').src = '/static/images/gold_rank.png'; 
                    }

                } else {
                    console.error("Reader not found");
                }
            })
            .catch(error => {
                console.error("Error fetching Reader:", error);
            });

            if (isDailyLogin=="true") {
                document.querySelector('header').style.marginBottom="1%";
                let alertBox = document.getElementById("gamefication_alert");
                alertBox.style.display = "flex";
            
                setTimeout(() => {
                    alertBox.style.display = "none";
                    document.querySelector('header').style.marginBottom="5.2%";
                    localStorage.removeItem('isDailyLogin');
                }, 5000); // Hide after 5 seconds
            }
            else{
                document.querySelector('header').style.marginBottom="5.2%";
                localStorage.removeItem('isDailyLogin');
            }
            
        } 
        else {
            console.log("No user_id found.");
        }

    } catch (error) {
        console.error('Invalid token:', error);
        localStorage.removeItem('jwt_token'); // Remove invalid token
        window.location.href = '/login'; // Redirect to login
    }
});


//---------------------------------------------------------------------------------------

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
    }, 200); // Delay of 100ms before closing
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
    window.location.href = '/search-page/?search=';
}
//---------------------------------------------------------------------------------------

// search:

document.getElementById('search-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') { // Check if the pressed key is 'Enter'
        const inputValue = this.value.trim(); // Get the input value and trim whitespace
        if (inputValue != '') {
            const search_input = encodeURIComponent(inputValue);
            const redirectUrl = `/search-page?search=${search_input}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
        } 

    }
});

//---------------------------------------------------------------------------------------

//-- fav-list --

const fav_list_Button = document.getElementById('fav_list');
const dropdown_fav_list = document.getElementById('fav_list_dropdown');
let closeTimeout_fav_list;
const favListImg = document.getElementById('img_fav_list');  // Correct image element selection

// Function to show the dropdown and change icon color
function showDropdown_fav_list() {
    clearTimeout(closeTimeout_fav_list);  // Cancel any scheduled closing
    dropdown_fav_list.style.display = 'block';
    favListImg.src = '/static/images/fav_list_yellow.png';  // Change icon to yellow
}

// Function to hide the dropdown with a delay and reset icon color
function hideDropdown_fav_list() {
    closeTimeout_fav_list = setTimeout(() => {
        dropdown_fav_list.style.display = 'none';
        favListImg.src = '/static/images/fav_list.png';  // Reset icon to original color
    }, 200);  // Delay of 100ms before closing
}

document.addEventListener('DOMContentLoaded', () => {
    // Event listener for when mouse enters the button
    fav_list_Button.addEventListener('mouseenter', () => {
        showDropdown_fav_list();

        const empty_wishList = document.getElementById('empty_wishList');
        const notEmpty_wishList = document.getElementById('notEmpty_wishList');

        empty_wishList.style.display = 'block';
        notEmpty_wishList.style.display = 'none';

        const wishList_1 = document.getElementById('wishList-item_1');
        const wishList_2 = document.getElementById('wishList-item_2');
        const wishList_3 = document.getElementById('wishList-item_3');
        

        wishList_1.style.display = 'none';
        wishList_2.style.display = 'none';
        wishList_3.style.display = 'none';

        const wishList = [
            document.getElementById('wishlist-item_1'),
            document.getElementById('wishlist-item_2'),
            document.getElementById('wishlist-item_3')
        ];

        
        wishList.forEach((wishListElement, index) => {
            if (wishListElement) { // Ensure the element exists
                wishListElement.addEventListener('click', () => {
                    window.location.href = `/`; // Example URL
                });
            }
        });
        

        // Fetch initial data when page loads
        fetch(`/getLastThreeWishListView?user_id=${userId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch wishList');
                }
                return response.json();
            })
            .then(data => {
                if(Array.isArray(data) && data.length === 0){
                    empty_wishList.style.display = 'block';
                    notEmpty_wishList.style.display = 'none';
                }
                else if(data){
                    empty_wishList.style.display = 'none';
                    notEmpty_wishList.style.display = 'block';

                    data.forEach((wishList, index) => {
                        const wishList_title = document.getElementById(`wishList-item_title_${index + 1}`);
                        const wishList_author = document.getElementById(`wishList-item_author_${index + 1}`);
                        const wishList_category = document.getElementById(`wishList-item_category_${index + 1}`);
                        const wishList_image=document.getElementById(`wishList-item_image_${index + 1}`);
                        const wishList_item = document.getElementById(`wishList-item_${index + 1}`);
                
                        // If there is data for the notification, display the notification item
                        if (wishList) {
                            wishList_item.style.display = 'flex'; // Make the notification item visible

                            // wishList details
                            wishList_title.textContent = wishList.book_name || 'Title...';
                            wishList_author.textContent = `Author: ${wishList.book_author || 'No Author'}`;
                            wishList_category.textContent = `Category: ${wishList.book_type || 'No Category'}`;
                
                            // image
                            if (wishList.book_image) {
                                wishList_image.src = wishList.book_image;
                            }

                            wishList_item.addEventListener('click', () => {
                                window.location.href = `/viewBookPage/${wishList.book_id}`;
                            });
                            
                        } else {
                            // If no data for the wishList, hide the book item
                            wishList_item.style.display = 'none';
                        }
                    });
                    
                }
                
            })
            .catch(error => {
                console.error('Error fetching notification:', error);
            });
        });
});

// Event listener for when mouse leaves the button
fav_list_Button.addEventListener('mouseleave', (event) => {
    if (!dropdown_fav_list.contains(event.relatedTarget)) {
        hideDropdown_fav_list();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_fav_list.addEventListener('mouseenter', () => {
    showDropdown_fav_list();
});

// Event listener for when mouse leaves the dropdown
dropdown_fav_list.addEventListener('mouseleave', (event) => {
    if (!fav_list_Button.contains(event.relatedTarget)) {
        hideDropdown_fav_list();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_fav_list(fav_list) {
    dropdown_fav_list.style.display = 'none';  // Hide dropdown after selection
}





//---------------------------------------------------------------------------------------

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
    fetch(`/getLastThreeNotificationListView?user_id=${userId}`)
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
                        notifi_title.textContent = notification.notification_title || 'Title...';
                        notifi_content.textContent = notification.notification_record || 'No content...';
            
                        // image
                        if (notification.notification_title=="Accept Uploaded Book") {
                            notifi_image.src = '/static/images/accept.png'; 
                        }
                        else if(notification.notification_title=="Rejected Uploaded Book"){
                            notifi_image.src = '/static/images/reject.png'; 
                        }
                        else if(notification.notification_title=="New Point Achievement"){
                            notifi_image.src = '/static/images/point.png'; 
                        }
                        
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

// Function to handle option click in the dropdown
function handleOptionClick_user(option) {
    if (option === 'Rank') { 
        window.location.href = '/rankPage';
    }
    else if(option === 'User Profile'){
        window.location.href = '/accountSettingsPage';
    }
    else if(option === 'My Uploaded Book'){
        window.location.href = '/myUploadedBookPage';
    }
    else if(option === 'Wish List'){
        window.location.href = '/wish-listPage';
    }
    else if(option === 'Notification'){
        window.location.href = '/notificationPage'; 
    }
    else if(option === 'Send FeedBack'){
        document.getElementById("feedback-stack").style.display = "flex";
    }
    else if(option === 'Log out'){
        localStorage.removeItem('jwt_token'); 
        window.location.href = '/login'; 
    }

}

document.getElementById("closeBtn").onclick = function() {
    document.getElementById("feedback-stack").style.display = "none";
}

window.onclick = function(event) {
    if (event.target === document.getElementById("feedback-stack")) {
        document.getElementById("feedback-stack").style.display = "none";
    }
}

document.getElementById("sendFeedback").onclick = function() {
    const feedbackText = document.getElementById("feedbackText").value;

    // Ensure userId is set
    if (!userId) {
        alert("User ID is missing. Please log in again.");
        return;
    }

    // Ensure feedback text is not empty
    if (feedbackText.trim() === '') {
        document.getElementById("feedbackText").style.borderColor = "red";
        return;
    }
    else{
        document.getElementById("feedbackText").style.borderColor = "";
    }

    // Log the data to verify it's being sent correctly
    console.log('Sending feedback:', { user_id: userId, feedback_description: feedbackText });

    // Sending feedback to the server via POST request
    fetch('/InsertFeedbackView/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            feedback_description: feedbackText
        }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error("Error sending feedback:", error);
        alert("There was an error sending your feedback.");
    });

    // Close the feedback stack after sending feedback
    document.getElementById("feedback-stack").style.display = "none";
    document.getElementById("feedbackText").value = '';

    document.getElementById("afterfeedback-stack").style.display = "flex";
}

document.getElementById("doneFeedback").onclick = function() {
    document.getElementById("afterfeedback-stack").style.display = "none";
}

document.getElementById("closeBtn2").onclick = function() {
    document.getElementById("afterfeedback-stack").style.display = "none";
}

//---------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------

//-- Advertisment --

const images = [
    "/static/images/0_advertisement_photo.png",
    "/static/images/1_advertisement_photo.png",
    "/static/images/2_advertisement_photo.png"
];

let currentImageIndex = 0;
let change_image_time = 25000;
const advertisementImage = document.getElementById('advertisement-image');
const prevButton = document.getElementById('prev');
const nextButton = document.getElementById('next');

// Function to update the image
function updateImage() {
    advertisementImage.src = images[currentImageIndex];

    // Hide prev button if it's the first image
    if (currentImageIndex === 0) {
        prevButton.classList.add('hidden');
    } else {
        prevButton.classList.remove('hidden');
    }

    // Hide next button if it's the last image
    if (currentImageIndex === images.length - 1) {
        nextButton.classList.add('hidden');
    } else {
        nextButton.classList.remove('hidden');
    }
}

// Function to reset the interval for auto-switching images
function resetImageInterval() {
    clearInterval(imageInterval);  // Clear the current interval
    imageInterval = setInterval(() => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        updateImage();
    }, change_image_time);  // Restart the interval
}

// Auto-switch images every 25 seconds
let imageInterval = setInterval(() => {
    currentImageIndex = (currentImageIndex + 1) % images.length;
    updateImage();
}, change_image_time);

// Event listeners for prev and next buttons
prevButton.addEventListener('click', (event) => {
    event.preventDefault();
    if (currentImageIndex > 0) {
        currentImageIndex--;
        updateImage();
        resetImageInterval();  // Reset the interval after manual change
    }
});

nextButton.addEventListener('click', (event) => {
    event.preventDefault();
    if (currentImageIndex < images.length - 1) {
        currentImageIndex++;
        updateImage();
        resetImageInterval();  // Reset the interval after manual change
    }
});

// Initial image setup
updateImage();

//---------------------------------------------------------------------------------------

// functionality for continue reading book

let currentData = null; 
let curr_url_continue=null;

document.addEventListener('DOMContentLoaded', () => {
    curr_url_continue=`/getContinue-reading-books?user_id=${userId}`;
    
    const book_continue_prev = document.getElementById('book_continue_prev');
    const book_continue_next = document.getElementById('book_continue_next');

    const book_continue_1 = document.getElementById('book_continue_item_1');
    const book_continue_2 = document.getElementById('book_continue_item_2');
    const book_continue_3 = document.getElementById('book_continue_item_3');
    const book_continue_4 = document.getElementById('book_continue_item_4');
    const book_continue_5 = document.getElementById('book_continue_item_5');

    // Initially hide all book items
    book_continue_1.style.display = 'none';
    book_continue_2.style.display = 'none';
    book_continue_3.style.display = 'none';
    book_continue_4.style.display = 'none';
    book_continue_5.style.display = 'none';

    // Fetch initial data when page loads
    fetch(`/getContinue-reading-books?user_id=${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch continue reading books');
            }
            return response.json();
        })
        .then(data => {
            if(data.count>0){
                document.getElementById('continue-reading-book-container').style.display="block";

                currentData = data; // Store the fetched data
                updateBookDetails(data); // Update the book details initially

                // Event listener for "Previous" button
                book_continue_prev.addEventListener('click', (event) => {
                    event.preventDefault(); // Prevent the default anchor behavior
                    console.log("prev: "+currentData.previous);
                    if (currentData.previous) {
                        curr_url_continue=currentData.previous;
                        loadBooks(curr_url_continue); // Load books for the previous page
                    }
                });

                // Event listener for "Next" button
                book_continue_next.addEventListener('click', (event) => {
                    event.preventDefault(); // Prevent the default anchor behavior
                    console.log("next: "+currentData.next);
                    if (currentData.next) {
                        curr_url_continue=currentData.next;
                        loadBooks(curr_url_continue); // Load books for the next page
                    }
                });
            }
            else{
                document.getElementById('continue-reading-book-container').style.display="none";
            }
            
        })
        .catch(error => {
            console.error('Error fetching continue reading books:', error);
        });
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
    const book_continue_prev = document.getElementById('book_continue_prev');
    const book_continue_next = document.getElementById('book_continue_next');

    const book_continue_1 = document.getElementById('book_continue_item_1');
    const book_continue_2 = document.getElementById('book_continue_item_2');
    const book_continue_3 = document.getElementById('book_continue_item_3');
    const book_continue_4 = document.getElementById('book_continue_item_4');
    const book_continue_5 = document.getElementById('book_continue_item_5');

    // Hide all book items initially
    book_continue_1.style.display = 'none';
    book_continue_2.style.display = 'none';
    book_continue_3.style.display = 'none';
    book_continue_4.style.display = 'none';
    book_continue_5.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_continue_prev.style.display = 'none';
        book_continue_next.style.display = 'none';
    } else if (data.previous == null && data.next != null) {
        book_continue_prev.style.display = 'none';
        book_continue_next.style.display = 'block';
    } else if (data.previous != null && data.next == null) {
        book_continue_prev.style.display = 'block';
        book_continue_next.style.display = 'none';
    } else {
        book_continue_prev.style.display = 'block';
        book_continue_next.style.display = 'block';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`book_continue_name_${index + 1}`);
        const bookAuthor = document.getElementById(`book_continue_author_${index + 1}`);
        const bookCategory = document.getElementById(`book_continue_category_${index + 1}`);
        const bookRating = document.getElementById(`book_continue_rating_${index + 1}`);
        const bookImage = document.getElementById(`book_continue_image_${index + 1}`);
        const bookItem = document.getElementById(`book_continue_item_${index + 1}`);
        const bookFavImage = document.getElementById(`book_continue_fav_${index + 1}`);

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

            // Check if the book is in the wishlist
            fetch(`/check-book-in-wishlist/?book_id=${book.book_id}&user_id=${userId}`)
                .then(response => response.json())
                .then(data => {
                    // If the book is in the wishlist, update the favorite image
                    if (data.in_wishlist) {
                        bookFavImage.src = '/static/images/fav_clicked.png'; 
                    } else {
                        bookFavImage.src = '/static/images/fav_not-click.png';
                    }
                })
                .catch(error => {
                    console.error('Error checking wishlist:', error);
                });

                bookItem.addEventListener('click', () => {
                    window.location.href = `/viewBookPage/${book.book_id}`;
                });
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}

//---------------------------------------------------------------------------------------

// Functionality for "fav_btn" continue reading
const favButtons_continue = document.querySelectorAll('[id^="favorite-btn_continue"]'); 
const favImgs_continue = document.querySelectorAll('[id^="favorite_img_continue"] img');

favButtons_continue.forEach((favButton, index) => {
    favButton.addEventListener('click', (event) => {
        event.stopPropagation();
        const favImg = favImgs_continue[index]; // Get the corresponding image
        
        // Get the book_id from currentData.results array
        const book = currentData.results[index]; // Access the book object based on the button clicked
        const bookId = book.book_id; // Get the book_id from the currentData


        if (favImg.src.includes('fav_not-click.png')) {
            // Add to wishlist
            fetch('/add-to-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_clicked.png'; // Change image to clicked state
                } else {
                    alert(data.error);
                }
            });
        } else {
            // Remove from wishlist
            fetch('/remove-from-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_not-click.png'; // Change image back to not clicked state
                } else {
                    alert(data.error);
                }
            });
        }

        updateBooks();
    });
});



//---------------------------------------------------------------------------------------
// functionality for most readed book

let currentData_most_readed = null; 
let curr_url_most_readed=null;

document.addEventListener('DOMContentLoaded', () => {
    curr_url_most_readed=`/getMostReadedPreferencesBook?user_id=${userId}`;

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


    // Fetch initial data when page loads
    fetch(`/getMostReadedPreferencesBook?user_id=${userId}`)
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
                    curr_url_most_readed=currentData_most_readed.previous;
                    loadBooks_most_readed(curr_url_most_readed); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_most_readed_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_most_readed.next);
                if (currentData_most_readed.next) {
                    curr_url_most_readed=currentData_most_readed.next;
                    loadBooks_most_readed(curr_url_most_readed); // Load books for the next page
                }
            });
        })
        .catch(error => {
            console.error('Error fetching most readed books:', error);
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
        const bookFavImage = document.getElementById(`book_most_readed_fav_${index + 1}`);

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

            // Check if the book is in the wishlist
            fetch(`/check-book-in-wishlist/?book_id=${book.book_id}&user_id=${userId}`)
                .then(response => response.json())
                .then(data => {
                    // If the book is in the wishlist, update the favorite image
                    if (data.in_wishlist) {
                        bookFavImage.src = '/static/images/fav_clicked.png'; 
                    } else {
                        bookFavImage.src = '/static/images/fav_not-click.png';
                    }
                })
                .catch(error => {
                    console.error('Error checking wishlist:', error);
            });

            bookItem.addEventListener('click', () => {
                window.location.href = `/viewBookPage/${book.book_id}`;
            });
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}


//---------------------------------------------------------------------------------------

// Functionality for "fav_btn" most readed
const favButtons_most_readed = document.querySelectorAll('[id^="favorite-btn_most_readed"]'); 
const favImgs_most_readed = document.querySelectorAll('[id^="favorite_img_most_readed"] img');

favButtons_most_readed.forEach((favButton, index) => {
    favButton.addEventListener('click', (event) => {
        event.stopPropagation();
        const favImg = favImgs_most_readed[index]; // Get the corresponding image
        
        // Get the book_id from currentData.results array
        const book = currentData_most_readed.results[index]; // Access the book object based on the button clicked
        const bookId = book.book_id; // Get the book_id from the currentData


        if (favImg.src.includes('fav_not-click.png')) {
            // Add to wishlist
            fetch('/add-to-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_clicked.png'; // Change image to clicked state
                } else {
                    alert(data.error);
                }
            });
        } else {
            // Remove from wishlist
            fetch('/remove-from-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_not-click.png'; // Change image back to not clicked state
                } else {
                    alert(data.error);
                }
            });
        }

        updateBooks();
    });
});


//---------------------------------------------------------------------------------------


// functionality for most rating book

let currentData_most_rating = null; 
let curr_url_most_rating=null;

document.addEventListener('DOMContentLoaded', () => {

    curr_url_most_rating=`/getMostRatingPreferencesBook?user_id=${userId}`;

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



    // Fetch initial data when page loads
    fetch(`/getMostRatingPreferencesBook?user_id=${userId}`)
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
                    curr_url_most_rating=currentData_most_rating.previous;
                    loadBooks_most_rating(curr_url_most_rating); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_most_rating_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_most_rating.next);
                if (currentData_most_rating.next) {
                    curr_url_most_rating=currentData_most_rating.next;
                    loadBooks_most_rating(curr_url_most_rating); // Load books for the next page
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
        const bookFavImage = document.getElementById(`book_most_rating_fav_${index + 1}`);

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

            // Check if the book is in the wishlist
            fetch(`/check-book-in-wishlist/?book_id=${book.book_id}&user_id=${userId}`)
                .then(response => response.json())
                .then(data => {
                    // If the book is in the wishlist, update the favorite image
                    if (data.in_wishlist) {
                        bookFavImage.src = '/static/images/fav_clicked.png'; 
                    } else {
                        bookFavImage.src = '/static/images/fav_not-click.png';
                    }
                })
                .catch(error => {
                    console.error('Error checking wishlist:', error);
            });

            bookItem.addEventListener('click', () => {
                window.location.href = `/viewBookPage/${book.book_id}`;
            });

        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}

//---------------------------------------------------------------------------------------

// Functionality for "fav_btn" most rating
const favButtons_most_rating = document.querySelectorAll('[id^="favorite-btn_most_rating"]'); 
const favImgs_most_rating = document.querySelectorAll('[id^="favorite_img_most_rating"] img');

favButtons_most_rating.forEach((favButton, index) => {
    favButton.addEventListener('click', (event) => {
        event.stopPropagation();
        const favImg = favImgs_most_rating[index]; // Get the corresponding image
        
        // Get the book_id from currentData.results array
        const book = currentData_most_rating.results[index]; // Access the book object based on the button clicked
        const bookId = book.book_id; // Get the book_id from the currentData


        if (favImg.src.includes('fav_not-click.png')) {
            // Add to wishlist
            fetch('/add-to-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_clicked.png'; // Change image to clicked state
                } else {
                    alert(data.error);
                }
            });
        } else {
            // Remove from wishlist
            fetch('/remove-from-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_not-click.png'; // Change image back to not clicked state
                } else {
                    alert(data.error);
                }
            });
        }

        updateBooks();
    });
});


//---------------------------------------------------------------------------------------

// functionality for last updated book

let currentData_last_updated = null; 
let curr_url_last_updated=null;

document.addEventListener('DOMContentLoaded', () => {

    curr_url_last_updated=`/getLastPreferencesUploadedBook?user_id=${userId}`;

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


    // Fetch initial data when page loads
    fetch(`/getLastPreferencesUploadedBook?user_id=${userId}`)
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
                    curr_url_last_updated=currentData_last_updated.previous;
                    loadBooks_last_updated(curr_url_last_updated); // Load books for the previous page
                }
            });

            // Event listener for "Next" button
            book_last_updated_next.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                console.log("next: "+currentData_last_updated.next);
                if (currentData_last_updated.next) {
                    curr_url_last_updated=currentData_last_updated.next;
                    loadBooks_last_updated(curr_url_last_updated); // Load books for the next page
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
        const bookFavImage = document.getElementById(`book_last_updated_fav_${index + 1}`);

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

            // Check if the book is in the wishlist
            fetch(`/check-book-in-wishlist/?book_id=${book.book_id}&user_id=${userId}`)
                .then(response => response.json())
                .then(data => {
                    // If the book is in the wishlist, update the favorite image
                    if (data.in_wishlist) {
                        bookFavImage.src = '/static/images/fav_clicked.png'; 
                    } else {
                        bookFavImage.src = '/static/images/fav_not-click.png';
                    }
                })
                .catch(error => {
                    console.error('Error checking wishlist:', error);
            });

            bookItem.addEventListener('click', () => {
                    window.location.href = `/viewBookPage/${book.book_id}`;
            });
        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}

//---------------------------------------------------------------------------------------

// Functionality for "fav_btn" last updated
const favButtons_last_updated = document.querySelectorAll('[id^="favorite-btn_last_updated"]'); 
const favImgs_last_updated = document.querySelectorAll('[id^="favorite_img_last_updated"] img');

favButtons_last_updated.forEach((favButton, index) => {
    favButton.addEventListener('click', (event) => {
        event.stopPropagation();
        const favImg = favImgs_last_updated[index]; // Get the corresponding image
        
        // Get the book_id from currentData.results array
        const book = currentData_last_updated.results[index]; // Access the book object based on the button clicked
        const bookId = book.book_id; // Get the book_id from the currentData


        if (favImg.src.includes('fav_not-click.png')) {
            // Add to wishlist
            fetch('/add-to-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_clicked.png'; // Change image to clicked state
                } else {
                    alert(data.error);
                }
            });
        } else {
            // Remove from wishlist
            fetch('/remove-from-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_id: bookId, user_id: userId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    favImg.src = '/static/images/fav_not-click.png'; // Change image back to not clicked state
                } else {
                    alert(data.error);
                }
            });
        }

        updateBooks();
    });
});







function updateBooks(){

    loadBooks(curr_url_continue);

    loadBooks_most_readed(curr_url_most_readed);

    loadBooks_most_rating(curr_url_most_rating);

    loadBooks_last_updated(curr_url_last_updated);
    
}