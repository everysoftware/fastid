'use strict';

import {authClient} from './dependencies.js';

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = new URLSearchParams();
            form.append('grant_type', 'password');
            form.append('username', document.getElementById("email").value);
            form.append('password', document.getElementById("password").value);
            form.append('scope', '*');
            form.append('client_id', '');
            const response = await authClient.post('/token', {}, form);
            if (response.ok) {
                location.reload();
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const password = document.getElementById("password").value;
            if (password !== document.getElementById("confirmPassword").value) {
                alert("Passwords do not match.");
                return;
            }
            const passwordRegex = /^((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,20})$/;
            if (!passwordRegex.test(password)) {
                alert("Password must be at least 8 characters long and include a number and a special character.");
                return;
            }
            const body = {
                email: document.getElementById("email").value,
                password: password,
                first_name: document.getElementById("name").value
            }
            const response = await authClient.post("/register", {}, body);
            if (response.ok) {
                location.assign("/login");
            }
        });
    }
});
