'use strict';

import {profileClient} from './dependencies.js';

document.addEventListener("DOMContentLoaded", () => {
    // Edit profile
    document.getElementById("editProfileForm").addEventListener("submit", async (event) => {
        event.preventDefault()
        const body = {
            first_name: document.getElementById("firstName").value, last_name: document.getElementById("lastName").value
        }
        const response = await profileClient.patch("/users/me/profile", {}, body);
        if (response) {
            alert('Profile updated successfully.');
            location.reload();
        }
    });
});
