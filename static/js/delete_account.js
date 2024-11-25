'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", () => {
    const confirmationText = document.getElementById("confirmationText");
    const deleteAccountBtn = document.getElementById("deleteAccountBtn");

    confirmationText.addEventListener("input", () => {
        if (confirmationText.value === "CONFIRM") {
            deleteAccountBtn.removeAttribute("disabled");
        } else {
            deleteAccountBtn.setAttribute("disabled", "true");
        }
    });

    document.getElementById("deleteAccountForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        if (confirmationText.value === "CONFIRM") {
            const response = await profileClient.delete("/users/me");
            if (response.ok) {
                alert("Your account has been deleted.");
                location.reload();
            } else {
                alert("Failed to delete the account. Please try again.");
            }
        }
    });
});
