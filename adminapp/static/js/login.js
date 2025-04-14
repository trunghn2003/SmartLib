register_btn=document.getElementById('register');
const login_btn=document.getElementById('login');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const error_msg=document.getElementById('error');


// click on login button
login_btn.addEventListener('click', async (event) => {
    event.preventDefault();

    if (emailInput.value === "" || passwordInput.value === "") {
        error_msg.textContent = "Please fill all fields.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    } 
    else{
        const response = await fetch('/login-api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: emailInput.value,
                user_password: passwordInput.value
            })
        });
    
       
        if(!response.ok){
            error_msg.textContent = "Invalid email or password.";
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        }
        else{
            error_msg.textContent = "Login Successfully";
            error_msg.style.color = "green";
            error_msg.style.display = 'block';
        }
    }


});


// for alert
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0'; // Fade out
            setTimeout(() => alert.remove(), 300); // Remove after fade
        }, 3000); // 3 seconds
    });
});