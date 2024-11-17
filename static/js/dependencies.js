import {backendUrl} from './config.js';
import {AuthClient} from './auth_client.js';
import {ProfileClient} from './profile_client.js';

export const authClient = new AuthClient(backendUrl);
export const profileClient = new ProfileClient(backendUrl);
