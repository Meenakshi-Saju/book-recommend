
import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class UserService {
    private currentUser = new BehaviorSubject<string>('');

    setUsername(username: string) {
        this.currentUser.next(username);
        localStorage.setItem('currentUser', username); // Persist user session
    }

    getUsername(): string {
        return this.currentUser.getValue() || localStorage.getItem('currentUser') || '';
    }

    getUsernameObservable(): Observable<string> {
        return this.currentUser.asObservable();
    }

    logout() {
        this.currentUser.next('');
        localStorage.removeItem('currentUser');
    }
}