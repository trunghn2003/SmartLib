//-- Auth Access --

let userId = -1;  
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('jwt_token');

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
        if (userId == -1) {
            console.log("No user_id found.");
        }         

    } catch (error) {
        console.error('Invalid token:', error);
        localStorage.removeItem('jwt_token'); // Remove invalid token
        window.location.href = '/login'; // Redirect to login
    }
});

//-----------------------------------------------------------------------------

let selectedCategories = new Set(); 
let selected_num = 0;

function toggleCard(card) {
    card.classList.toggle('selected');
    
    const preferenceId = card.getAttribute('preference');
    const selectedText = document.getElementById('selected');
    const continueBtn = document.querySelector('.btn-continue');

    if (card.classList.contains('selected')) {
        selected_num++;
        selectedCategories.add(preferenceId);
    } else {
        selected_num--;
        selectedCategories.delete(preferenceId);
    }

    // Update the text dynamically
    if (selected_num >= 3) {
        selectedText.innerHTML = "Selected: " + selected_num;
        continueBtn.style.backgroundColor = "#3f48cc";
        continueBtn.style.cursor = "pointer";
        continueBtn.addEventListener('mouseover', function () {
            continueBtn.style.backgroundColor = "#575fd5";
        });
        continueBtn.addEventListener('mouseleave', function () {
            continueBtn.style.backgroundColor = "#3f48cc";
        });

        continueBtn.addEventListener('click', () => {

            fetch("/save_preferences/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `preferences=${Array.from(selectedCategories).join(',')}&user_id=${userId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    window.location.href = '/homePage';
                } else {
                    alert(data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    } else {
        selectedText.innerHTML = "Selected: " + selected_num + "/3 &nbsp; (minimum required: 3)";
        continueBtn.style.backgroundColor = "#b7b7b7";
        continueBtn.style.cursor = "not-allowed";

        continueBtn.addEventListener('mouseover', function () {
            continueBtn.style.backgroundColor = "#989696";
        });
        continueBtn.addEventListener('mouseleave', function () {
            continueBtn.style.backgroundColor = "#b7b7b7";
        });

        
    }
}
