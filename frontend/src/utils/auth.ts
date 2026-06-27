export interface AuthData {
    token: string;
    user: {
        username: string;
        name?: string;
        profession?: string;
        age?: string;
    };
}

export function saveAuth(data: AuthData): void {
    localStorage.setItem('factora_token', data.token);
    localStorage.setItem('factora_user', JSON.stringify(data.user));
    localStorage.setItem('factora_guest', 'false');
}

export function getToken(): string | null {
    return localStorage.getItem('factora_token');
}

export function getUser(): any {
    const stored = localStorage.getItem('factora_user');
    return stored ? JSON.parse(stored) : null;
}

export function logout(): void {
    localStorage.removeItem('factora_token');
    localStorage.removeItem('factora_user');
    localStorage.setItem('factora_guest', 'true');
    localStorage.removeItem('auth_method');
    window.location.reload();
}

export function isAuthenticated(): boolean {
    return !!getToken();
}
