const send_email = document.getElementById('send_email');
const another_email_msg = document.getElementById('another_email_msg');
const countdown = document.getElementById('countdown');
let count = 0;
let min = 0;
let sec = 0;

send_another_email();

// Add event listener to the link
send_email.addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default link behavior

    send_email.classList.add('hidden');
    another_email_msg.classList.remove('hidden'); // Show the cooldown message

    if (count === 0) {
        send_another_email();
        startCountdown(0, 59); // Start with 59 seconds
        count++;
    } else if (count === 1) {
        send_another_email();
        startCountdown(15, 0); // Start with 15 minutes
        count++;
    } else if (count > 1) {
        send_another_email();
        startCountdown(59, 59); // Start with 59 minutes, 59 seconds
        count++;
    }
});

// Countdown function
function startCountdown(startMin, startSec) {
    min = startMin;
    sec = startSec;

    const interval = setInterval(() => {
        if (sec === 0) {
            if (min === 0) {
                clearInterval(interval);
                another_email_msg.classList.add('hidden'); // Hide the message
                send_email.classList.remove('hidden');
            } else {
                min--; // Decrease minute
                sec = 59; // Reset seconds to 59
            }
        } else {
            sec--; // Decrease seconds
        }

        // Update the countdown text
        countdown.textContent = `${min}:${sec < 10 ? '0' + sec : sec} ${min > 0 ? 'minutes' : 'seconds'}`;
    }, 1000);
}

// Function to send another email
function send_another_email() {
    const url = send_email.getAttribute('href'); // Get the URL from the href attribute

    // Make an AJAX request to the backend
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest', // Inform the server it's an AJAX request
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message); // Handle the response (e.g., show a success message)
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}
