import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-book-recommendation',
    templateUrl: './book-recommendation.component.html',
    styleUrls: ['./book-recommendation.component.css']
})
export class BookRecommendationComponent {

    searchQuery: string = '';
    bookDetails: any = null;

    constructor(private http: HttpClient, private router: Router) { }
    searchBook(): void {
        if (!this.searchQuery.trim()) {
            return;
        }

        this.http.get<any>(`http://localhost:5000/search-book?query=${this.searchQuery}`)
            .subscribe(response => {
                console.log("Response from /search-book:", response); // Log the full response

                if (response.success) {
                    this.bookDetails = response.data[0];
                    console.log("Navigating with bookDetails:", this.bookDetails); // Log book details to be passed

                    this.router.navigate(['/search-details'], {
                        queryParams: {
                            title: this.bookDetails.title,
                            author: this.bookDetails.author,
                            description: this.bookDetails.description,
                            genre: this.bookDetails.genre,
                            url: this.bookDetails.url
                        }
                    });
                } else {
                    alert(response.message);
                    this.bookDetails = null;
                }
            }, error => {
                console.error('Error fetching book details:', error); // Log any HTTP errors
                alert('Error fetching book details');
            });
    }


    // searchBook(): void {
    //     if (!this.searchQuery.trim()) {
    //         return;
    //     }

    //     this.http.get<any>(`http://localhost:5000/search-book?query=${this.searchQuery}`)
    //         .subscribe(response => {
    //             if (response.success) {
    //                 this.bookDetails = response.data[0];  
    //                 this.router.navigate(['/book-detail'], { state: { bookDetails: this.bookDetails } });
    //             } else {
    //                 alert(response.message);
    //                 this.bookDetails = null;
    //             }
    //         }, error => {
    //             alert('Error fetching book details');
    //         });
    // }

    isGiveRecFormVisible = false;
    isTakeRecFormVisible = false;



    showGiveRecForm() {
        this.isGiveRecFormVisible = true;
        this.isTakeRecFormVisible = false;
        this.router.navigate(['/give-recommendation']);
    }

    showTakeRecForm() {
        this.isTakeRecFormVisible = true;
        this.isGiveRecFormVisible = false;
        this.router.navigate(['/take-recommendation']);
    }

}