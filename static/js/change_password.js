'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("changePasswordForm").addEventListener("submit", async (e) => {
        e.preventDefault();

        const newPassword = document.getElementById("newPassword").value;
        const confirmNewPassword = document.getElementById("confirmNewPassword").value;

        if (newPassword !== confirmNewPassword) {
            alert("New password and confirmation do not match.");
            return;
        }

        const passwordRegex = /^((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,20})$/;
        if (!passwordRegex.test(newPassword)) {
            alert("Password must be at least 8 characters long and include a number and a special character.");
            return;
        }

        const body = {
            password: newPassword,
        };
        const response = await profileClient.patch("/users/me/password", {}, body);

        if (response) {
            alert("Password changed successfully!");
            location.assign("/profile");
        }
    });
    document.getElementById("changePasswordBtn").addEventListener("click", () => {
        document.getElementById("changePasswordForm").requestSubmit();
    });
});
