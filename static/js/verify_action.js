'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", async () => {
    await profileClient.post("/notify/otp");
    document.getElementById("nextButton").addEventListener("click", async (e) => {
        e.preventDefault();
        const code = document.getElementById("fullCodeInput").value;
        if (code.length !== 6) {
            alert("Please enter the complete verification code.");
            return;
        }
        const body = {
            code: code,
        };
        const response = await profileClient.post("/notify/verify-token", {}, body);
        if (response.ok) {
            location.reload();
        }
    });
});
