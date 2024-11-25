'use strict';

export class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, params = {}, method = 'GET', body = null, headers = {}) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
        const options = {
            method, headers: headers, credentials: 'include'
        };

        if (body) {
            if (body.constructor === Object) {
                options.body = JSON.stringify(body);
                options.headers['Content-Type'] = 'application/json';
            } else if (body.constructor === URLSearchParams) {
                options.body = body;
                options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
            } else {
                options.body = body;
            }
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    const data = await response.json();
                    this.handleErrors(response, data);
                } else {
                    alert(`The server is unavailable. Please try again.\n\nError #${response.status} ${response.statusText} (server_unavailable)\n\n`);
                }
            }
            return response
        } catch (error) {
            console.error('Network error:', error);
            alert('A network error occurred. Please try again.\n\nError #0 Network error (network_error)');
            return null;
        }
    }

    handleErrors(response, data) {
        if (response.status === 422) {
            data = data[0];
        }
        const msg = data.msg, code = data.type;
        alert(`${msg}\n\nError #${response.status} ${response.statusText} (${code})`);
    }

    async post(endpoint, params = {}, body = {}, headers = {}) {
        return await this.request(endpoint, params, 'POST', body, headers);
    }

    async get(endpoint, params = {}, headers = {}) {
        return await this.request(endpoint, params, 'GET', null, headers);
    }

    async put(endpoint, params = {}, body = {}, headers = {}) {
        return await this.request(endpoint, params, 'PUT', body, headers);
    }

    async patch(endpoint, params = {}, body = {}, headers = {}) {
        return await this.request(endpoint, params, 'PATCH', body, headers);
    }

    async delete(endpoint, params = {}, headers = {}) {
        return await this.request(endpoint, params, 'DELETE', null, headers);
    }

}
