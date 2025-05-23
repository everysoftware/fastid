'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", () => {
    const codeInputContainer = document.getElementById("codeInputContainer");
    const confirmButton = document.getElementById("confirmButton");

    document.getElementById("sendCodeForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const params = {action: "recover-password", email: email};
        const response = await profileClient.post("/otp/send", params);
        if (response.ok) {
            codeInputContainer.classList.remove("d-none");
            confirmButton.disabled = false;
        }
    });

    document.getElementById("restoreAccountForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const code = document.getElementById("fullCodeInput").value;
        const body = {action: "recover-password", code: code, email: email};
        const response = await profileClient.post("/otp/verify", {}, body);
        if (response.ok) {
            location.assign("/verify-action?action=change-password");
        }
    });
});
