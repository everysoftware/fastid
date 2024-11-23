import {profileClient} from './dependencies.js';

document.addEventListener("DOMContentLoaded", () => {
    // Edit profile
    let form = document.getElementById("editProfileForm");
    form.addEventListener("submit", async function (event) {
        event.preventDefault()
        const firstName = document.getElementById("firstName").value;
        const lastName = document.getElementById("lastName").value;
        const response = await profileClient.patch("/users/me/profile", {}, {
            first_name: firstName,
            last_name: lastName
        });
        if (response) {
            alert('Profile updated successfully.');
            location.reload();
        }
    });
    document.getElementById("editProfileBtn").addEventListener("click", function () {
        form.requestSubmit();
    });
});
