import {profileClient} from './dependencies.js';

(function () {
    'use strict'
    // Edit profile
    let form = document.getElementById("editProfileForm");
    form.addEventListener("submit", async function (event) {
        event.preventDefault()
        const firstName = document.getElementById("firstName").value;
        const lastName = document.getElementById("lastName").value;
        const response = await profileClient.patch("/me/profile", {}, {first_name: firstName, last_name: lastName});
        if (response) {
            alert('Profile updated successfully.');
            location.reload();
        }
    });
    document.getElementById("editProfileBtn").addEventListener("click",  function () {
        form.requestSubmit();
    });
    // Change email
    const modalError = document.getElementById('modalError');
    form = document.getElementById("changeEmailForm");
    form.addEventListener("submit", async function (event) {
        event.preventDefault()
        const response = await profileClient.post("/notifier/otc", {}, {});
        if (!response.ok) {
            modalError.textContent = 'An error occurred. Please try again.';
            modalError.classList.remove('d-none');
        }
    });
    document.getElementById("changeEmailBtn").addEventListener("click",  function () {
        form.requestSubmit();
    });
    document.getElementById('confirmActionBtn').addEventListener("click", async () => {
        const otpInputs = document.querySelectorAll('.otp-input');
        const code = Array.from(otpInputs).map(input => input.value).join('');
        const email = document.getElementById('email').value;
        if (code.length !== 6) {
            modalError.textContent = 'Please enter the 6-digit code.';
            modalError.classList.remove('d-none');
            return;
        }
        try {
            const response = await profileClient.patch("/me/email", {}, {email: email, code: code});
            if (response.ok) {
                alert('Email updated successfully.');
                location.reload();
            } else {
                throw new Error('Invalid code');
            }
        } catch (error) {
            modalError.textContent = error.message || 'An error occurred. Please try again.';
            modalError.classList.remove('d-none');
        }
    });
})()
