'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", () => {
    const codeInputContainer = document.getElementById("codeInputContainer");
    const confirmButton = document.getElementById("confirmButton");

    document.getElementById("sendCodeForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("newEmail").value;
        const params = {new_email: email};
        const response = await profileClient.post("/notify/otp", params);
        if (response.ok) {
            codeInputContainer.classList.remove("d-none");
            confirmButton.disabled = false;
        }
    });

    document.getElementById("emailChangeForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("newEmail").value;
        const code = document.getElementById("fullCodeInput").value;
        const body = {code: code, new_email: email};
        const response = await profileClient.patch("/users/me/email", {}, body);
        if (response.ok) {
            alert("Email updated successfully!");
            location.assign("/profile");
        }
    });
});
