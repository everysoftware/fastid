'use strict';

import {profileClient} from "./dependencies.js";

document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');
    await profileClient.post(`/otp/send?action=${action}`);
    document.getElementById("nextButton").addEventListener("click", async (e) => {
        e.preventDefault();
        const code = document.getElementById("fullCodeInput").value;
        if (code.length !== 6) {
            alert("Please enter the complete verification code.");
            return;
        }
        const body = {
            action: action,
            code: code,
        };
        const response = await profileClient.post("/otp/verify", {}, body);
        if (response.ok) {
            location.reload();
        }
    });
});
