// src/app/components/login/login.component.ts
import { Component, AfterViewInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { UserService } from '../../services/user.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css']
})
export class LoginComponent implements AfterViewInit {
    ngAfterViewInit(): void {
        const switchers = Array.from(document.querySelectorAll('.switcher'));

        switchers.forEach((item) => {
            item.addEventListener('click', () => {
                switchers.forEach((switcher) =>
                    switcher.parentElement?.classList.remove('is-active')
                );
                item.parentElement?.classList.add('is-active');
            });
        });
    }
    username: string = '';
    password: string = '';
    confirmPassword: string = '';
    selectedGenres: string[] = [];  // Updated to hold selected genres
    notes: string = '';

    constructor(
        private authService: AuthService,
        private userService: UserService,
        private router: Router
    ) { }

    login() {
        console.log('Attempting login with username:', this.username);

        this.authService.loginUser({ username: this.username, password: this.password }).subscribe(
            (response: any) => {
                if (response.success) {
                    console.log('Login successful:', response.message);
                    this.userService.setUsername(this.username);  // Store username in UserService
                    alert(response.message);

                    this.router.navigate(['/main-page']);
                } else {
                    console.log('Login failed:', response.message);
                    alert(response.message);
                }
            },
            error => {
                console.error('Login error:', error);
                alert('An error occurred. Please try again later.');
            }
        );
    }

    toggleGenre(genre: string) {
        const index = this.selectedGenres.indexOf(genre);
        if (index > -1) {
            this.selectedGenres.splice(index, 1);
        } else {
            this.selectedGenres.push(genre);
        }
    }

    register() {
        if (this.password !== this.confirmPassword) {
            alert('Passwords do not match.');
            return;
        }

        this.authService.registerUser({
            username: this.username,
            password: this.password
        }).subscribe(response => {
            if (response.success) {
                this.userService.setUsername(this.username);  // Store username in UserService
                alert('Registration successful!');
                this.router.navigate(['/main-page']);
            } else {
                alert('Registration failed: ' + response.message);
            }
        }, error => {
            console.error('Registration error:', error);
            alert('An error occurred. Please try again later.');
        });

    }
}



// import { Component, AfterViewInit } from '@angular/core';

// @Component({
//     selector: 'app-login',
//     templateUrl: './login.component.html',
//     styleUrls: ['./login.component.css']
// })
// export class Home1Component implements AfterViewInit {
//     ngAfterViewInit(): void {
//         const switchers = Array.from(document.querySelectorAll('.switcher'));

//         switchers.forEach((item) => {
//             item.addEventListener('click', () => {
//                 switchers.forEach((switcher) =>
//                     switcher.parentElement?.classList.remove('is-active')
//                 );
//                 item.parentElement?.classList.add('is-active');
//             });
//         });
//     }
// }