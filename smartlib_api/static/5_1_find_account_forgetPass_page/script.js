const emailInput = document.getElementById('email');
const search_btn = document.getElementById('search_btn');
const error_msg = document.getElementById('error');


search_btn.addEventListener('click', async (event) => {
    event.preventDefault();

    if(emailInput.value === ""){
        error_msg.textContent = "Please fill the field.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    }
    else{
        const response = await fetch('/check-email-api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
            })
        });
    
        if (!response.ok) {
            const data = await response.json();
            error_msg.textContent = data.message;
            error_msg.style.color = "red";
            error_msg.style.display = "block";
        } else {
            const email = encodeURIComponent(emailInput.value);
            const redirectUrl = `/confirm_email_change_password?email=${email}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
            error_msg.style.display = "none";
        }
    }
    
});