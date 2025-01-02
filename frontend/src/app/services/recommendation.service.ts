import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { UserService } from './user.service';
@Injectable({
    providedIn: 'root'
})
export class RecommendationService {
    private apiUrl = 'http://127.0.0.1:5000';
    private newRecommendationSubject = new Subject<boolean>();
    private currentUsername = new BehaviorSubject<string>('');


    constructor(private http: HttpClient, private userService: UserService) {
        this.currentUsername.next(this.userService.getUsername() || '');

        this.userService.getUsernameObservable().subscribe(newUsername => {
            this.currentUsername.next(newUsername);
        });
    }  // Inject UserService

    getRecommendation(userPreferences: any): Observable<any> {
        const username = this.currentUsername.getValue();
        console.log('Getting recommendation for user:', username); // Debug log
        return this.http.post(`${this.apiUrl}/recommend`, { username, ...userPreferences });
    }

    giveRecommendation(data: any): Observable<any> {
        const username = this.userService.getUsername();  // Retrieve the username from UserService
        const requestData = { username, ...data };
        return this.http.post(`${this.apiUrl}/give-recommendation`, requestData);
    }

    getPlaylistForBook(bookTitle: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/song-recommendation`, { book: bookTitle });
    }



    submitFeedback(username: string, bookTitle: string, feedbackType: string, value: boolean): Observable<any> {
        const currentUser = this.currentUsername.getValue();
        if (currentUser !== username) {
            console.warn('Username mismatch in feedback submission');
            username = currentUser;
        }
        console.log('Submitting feedback:', { username, bookTitle, feedbackType, value });
        const payload = {
            username,
            bookTitle,
            feedbackType,
            value
        };
        return this.http.post(`${this.apiUrl}/book-feedback`, payload);
    }

    getUserFeedback(username: string, bookTitle: string): Observable<any> {
        return this.http.get(`${this.apiUrl}/get-user-interactions`, {
            params: {
                username,
                bookTitle
            }
        });
    }

    setUsername(username: string) {
        this.currentUsername.next(username);
    }

    getUsername(): Observable<string> {
        return this.currentUsername.asObservable();
    }

    triggerNewRecommendation(username: string): void {
        // Verify username matches current user
        const currentUser = this.currentUsername.getValue();
        if (currentUser !== username) {
            console.warn('Username mismatch in recommendation trigger');
            username = currentUser;
        }

        this.newRecommendationSubject.next(true);
        this.getRecommendation({ username }).subscribe();
    }


    getNewRecommendationTrigger(): Observable<boolean> {
        return this.newRecommendationSubject.asObservable();
    }
}

