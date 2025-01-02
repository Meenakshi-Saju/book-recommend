// import { Injectable } from '@angular/core';
// import { HttpClient, HttpHeaders } from '@angular/common/http';
// import { Observable } from 'rxjs';

// interface RegisterData {
//     username: string;
//     password: string;
//     genres: string[];
//     notes: string;
// }

// interface LoginData {
//     username: string;
//     password: string;
// }

// @Injectable({
//     providedIn: 'root'
// })
// export class AuthService {
//     private baseUrl = 'http://localhost:5000';  // Flask API base URL

//     constructor(private http: HttpClient) { }

//     registerUser(data: RegisterData): Observable<any> {
//         const url = `${this.baseUrl}/register`;
//         return this.http.post(url, data, {
//             headers: new HttpHeaders({
//                 'Content-Type': 'application/json'
//             })
//         });
//     }

//     loginUser(credentials: { username: string, password: string }): Observable<any> {
//         return this.http.post(`${this.baseUrl}/login`, credentials);
//     }
// }



// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { UserService } from './user.service';
interface RegisterData {
    username: string;
    password: string;
    genres?: string[];  // Add genres as an optional field
    notes?: string;
}

interface LoginData {
    username: string;
    password: string;
}

interface PreferencesData {
    username: string;
    genres: string[];
    notes: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private baseUrl = 'http://127.0.0.1:5000';


    constructor(private http: HttpClient, private userService: UserService) { }  // Inject UserService

    registerUser(data: RegisterData): Observable<any> {
        const url = `${this.baseUrl}/register`;
        return this.http.post(url, data, {
            headers: new HttpHeaders({
                'Content-Type': 'application/json'
            })
        }).pipe(
            tap((response: any) => {
                // Set the username in UserService if registration is successful
                if (response.success) {
                    this.userService.setUsername(data.username);
                }
            })
        );
    }

    loginUser(credentials: LoginData): Observable<any> {
        return this.http.post(`${this.baseUrl}/login`, credentials).pipe(
            tap((response: any) => {
                // Set the username in UserService if login is successful
                if (response.success) {
                    this.userService.setUsername(credentials.username);
                }
            })
        );
    }
    saveGenresAndNotes(data: PreferencesData): Observable<any> {
        const url = `${this.baseUrl}/save-preferences`;
        return this.http.post(url, data, {
            headers: new HttpHeaders({ 'Content-Type': 'application/json' })
        });
    }


}
