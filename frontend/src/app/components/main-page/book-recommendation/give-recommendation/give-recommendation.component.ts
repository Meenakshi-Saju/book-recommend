import { Component } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
    selector: 'app-give-recommendation',
    templateUrl: './give-recommendation.component.html',
    styleUrls: ['./give-recommendation.component.css']
})
export class GiveRecommendationComponent {
    bookName = '';
    authorName = '';
    genre = '';
    description = '';
    isSubmitted = false;
    submissionMessage = '';
    isError: boolean = false;  // New flag to handle error styling


    constructor(private http: HttpClient, private router: Router) { }  // Inject Router


    submitGiveRec() {
        const recommendationData = {
            bookName: this.bookName,
            authorName: this.authorName,
            description: this.description,
            genre: this.genre,
        };

        this.http.post<any>('http://localhost:5000/add-recommendation', recommendationData)
            .subscribe({
                next: (response) => {
                    this.isSubmitted = true;
                    this.isError = false;
                    this.submissionMessage = response.message || 'Recommendation submitted successfully!';
                    console.log('Recommendation Submitted:', recommendationData);

                    // Optional: Clear the form after successful submission
                    this.clearForm();
                },
                error: (error: HttpErrorResponse) => {
                    console.error('Error submitting recommendation:', error);
                    this.isSubmitted = true;
                    this.isError = true;

                    if (error.status === 409) {
                        // Duplicate book case
                        this.submissionMessage = 'This book already exists in our recommendations.';
                    } else if (error.error && error.error.message) {
                        // Use server-provided error message
                        this.submissionMessage = error.error.message;
                    } else {
                        // Generic error message
                        this.submissionMessage = 'Error submitting recommendation. Please try again.';
                    }
                }
            });
    }

    clearForm() {
        this.bookName = '';
        this.authorName = '';
        this.description = '';
        this.genre = '';
    }

    goBack() {
        this.router.navigate(['/book-recommendation']);
    }
}
