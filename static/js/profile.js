import {profileClient} from './dependencies.js';

(function () {
    'use strict'

    const editProfileForm = document.getElementById('editProfileForm');
    editProfileForm.addEventListener('submit', async function (event) {
        event.preventDefault()
        if (!editProfileForm.checkValidity()) {
            event.stopPropagation()
            editProfileForm.classList.add('was-validated')
            return;
        }
        const firstName = document.getElementById("firstName").value;
        const lastName = document.getElementById("lastName").value;
        const response = await profileClient.patch("/users/me", {}, {first_name: firstName, last_name: lastName});
        if (response) {
            location.reload();
        }
    });
    document.getElementById("editProfileBtn").addEventListener("click", function (event) {
        editProfileForm.requestSubmit();
    });
})()
