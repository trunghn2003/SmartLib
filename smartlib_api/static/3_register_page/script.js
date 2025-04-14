const register_btn = document.getElementById('register_btn');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirm_passwordInput = document.getElementById('confirm-password');
const error_msg = document.getElementById('error');
let valid_password_strong=false;
const redirectUrl = register_btn.getAttribute('data-redirect-url');
let hasErrors = false;

register_btn.addEventListener('click', async (event) => {
    event.preventDefault();
    hasErrors = false; 
    error_msg.style.display = "none"; 

    // Form validation
    if (nameInput.value === "" || emailInput.value === "" || passwordInput.value === "" || confirm_passwordInput.value === "") {
      hasErrors = true;
      error_msg.textContent = "Please fill all fields.";
      error_msg.style.color = "red";
      error_msg.style.display = 'block';
    } 
    else {
        if(valid_password_strong){
            const nameError = validateName(nameInput.value);
            const emailError = validateEmail(emailInput.value);
            const passwordError = validatePasswords(passwordInput.value, confirm_passwordInput.value);

            if (nameError !== "") {
                hasErrors = true;
                error_msg.textContent = nameError;
                error_msg.style.color = "red";
                error_msg.style.display = 'block';
            }
            else if (emailError !== "") {
                hasErrors = true;
                error_msg.textContent = emailError;
                error_msg.style.color = "red";
                error_msg.style.display = 'block';
            }
            else if (passwordError !== "") {
                hasErrors = true;
                error_msg.textContent = passwordError;
                error_msg.style.color = "red";
                error_msg.style.display = 'block';
            }
        }
        else{
            hasErrors = true;
            error_msg.textContent = "Use a strong password for better security.";
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        }
      
    }
  
    if (!hasErrors && valid_password_strong){ // Only execute reCAPTCHA if NO errors and valid password strong
        grecaptcha.reset(); // Reset reCAPTCHA for a fresh token
        grecaptcha.execute(); // Trigger reCAPTCHA again
    }
});

async function onSubmit(token) {
    if(!hasErrors){
        const response = await fetch('/register-api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_name: nameInput.value,
                email: emailInput.value,
                user_password: passwordInput.value,
                recaptcha_token: token
            })
        });
    
        if (!response.ok) {
            const data = await response.json();
            error_msg.textContent = data.error || "An unexpected error occurred.";
            error_msg.style.color = "red";
            error_msg.style.display = "block";
            grecaptcha.reset();
        } else {
            error_msg.textContent = "Created Account Successfully";
            error_msg.style.color = "green";
            error_msg.style.display = 'block';
            const data = await response.json(); // Get email from the response
            const email = encodeURIComponent(data.email); // Encode the email to be URL-safe
            const redirectUrl = `/confirm_email_register?email=${email}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
            error_msg.style.display = "none";
        }
    }
}


// Validation functions
function validateName(name) {
    if (name.length < 2) {
        return "Name must be at least 2 characters long.";
    } else if (/^\d/.test(name)) {
        return "Name cannot start with a number.";
    }
    return "";
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        return "Please enter a valid email address.";
    }
    else{
        return "";
    }
    
}


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