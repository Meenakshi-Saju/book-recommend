import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserService } from './user.service';
@Injectable({
    providedIn: 'root'
})
export class RecommendationService {
    private apiUrl = 'http://127.0.0.1:5000';


    constructor(private http: HttpClient, private userService: UserService) { }  // Inject UserService

    getRecommendation(userPreferences: any): Observable<any> {
        const username = this.userService.getUsername();  // Retrieve the username from UserService
        const requestData = { username, ...userPreferences };
        return this.http.post(`${this.apiUrl}/get-recommendation`, requestData);
    }

    giveRecommendation(data: any): Observable<any> {
        const username = this.userService.getUsername();  // Retrieve the username from UserService
        const requestData = { username, ...data };
        return this.http.post(`${this.apiUrl}/give-recommendation`, requestData);
    }

    getPlaylistForBook(bookTitle: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/song-recommendation`, { book: bookTitle });
    }

}

