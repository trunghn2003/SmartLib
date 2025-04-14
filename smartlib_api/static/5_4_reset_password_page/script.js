const passwordInput = document.getElementById('password');
const confirm_passwordInput = document.getElementById('confirm-password');
const error_msg = document.getElementById('error');
const reset_btn = document.getElementById('reset_btn');
let valid_password_strong=false;

const url = window.location.href;

// Extract the email part
const urlParts = url.split('/');
const email = urlParts[urlParts.length - 2];

reset_btn.addEventListener('click', async (event) => {
    event.preventDefault();
    error_msg.style.display = "none"; 

    if (passwordInput.value === "" || confirm_passwordInput.value === "") {
        error_msg.textContent = "Please fill all fields.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    } else {
        if (valid_password_strong) {
            const passwordError = validatePasswords(passwordInput.value, confirm_passwordInput.value);
            if (passwordError !== "") {
                error_msg.textContent = passwordError;
                error_msg.style.color = "red";
                error_msg.style.display = 'block';
            } else {
                error_msg.style.display = 'none';
                try {
                    const response = await fetch('/reset-password-api', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: email,
                            user_password: passwordInput.value
                        })
                    });

                    if (response.ok) {
                        // Redirect to login page on success
                        window.location.href = '/login';
                    } else if (response.status === 404) {
                        error_msg.textContent = "User not found.";
                        error_msg.style.color = "red";
                        error_msg.style.display = 'block';
                    } else {
                        error_msg.textContent = "An error occurred. Please try again.";
                        error_msg.style.color = "red";
                        error_msg.style.display = 'block';
                    }
                } catch (error) {
                    error_msg.textContent = "An error occurred. Please check your connection.";
                    error_msg.style.color = "red";
                    error_msg.style.display = 'block';
                }
            }
        } else {
            error_msg.textContent = "Use a strong password for better security.";
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        }
    }
});




function validatePasswords(password, confirmPassword) {
    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }
    return "";
}

passwordInput.addEventListener("input", updatePasswordStrength);

// Function to display password strength feedback
function updatePasswordStrength() {
    const password = passwordInput.value;

    // Check password strength using zxcvbn
    const strength = zxcvbn(password);

    // Update feedback based on the score
    switch (strength.score) {
        case 0:
            error_msg.style.display = 'block';
            error_msg.textContent = "Very Weak";
            error_msg.style.color = "red";
            valid_password_strong=false;
            break;
        case 1:
            error_msg.style.display = 'block';
            error_msg.textContent = "Weak";
            error_msg.style.color = "orange";
            valid_password_strong=false;
            break;
        case 2:
            error_msg.style.display = 'block';
            error_msg.textContent = "Strong";
            error_msg.style.color = "yellow";
            valid_password_strong=false;
            break;
        case 3:
            error_msg.style.display = 'block';
            error_msg.textContent = "Very Strong";
            error_msg.style.color = "darkgreen";
            valid_password_strong=true;
            break;
    }
}
