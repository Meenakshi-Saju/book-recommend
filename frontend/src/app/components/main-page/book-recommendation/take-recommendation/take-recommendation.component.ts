// src/app/components/take-recommendation/take-recommendation.component.ts
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../../../../services/user.service';

interface Book {
    title: string;
    author: string;
    genre: string;
    description: string;
    url: string;
    match_scores: {
        overall_match: number;
        notes_match: number;
        genre_match: number;
        feedback_match: number;
    };
}

interface RecommendationResponse {
    success: boolean;
    data: {
        book: Book;
        playlist: Array<{
            song: string;
            artist: string;
            year: number;
            popularity: number;
            danceability: number;
            energy: number;
            valence: number;
            tempo: number;
            genre: string;
        }>;
        match_scores: {
            overall_match: number;
            notes_match: number;
            genre_match: number;
            feedback_match: number;
        };
    };
    message?: string;
}

@Component({
    selector: 'app-take-recommendation',
    templateUrl: './take-recommendation.component.html',
    styleUrls: ['./take-recommendation.component.css']
})
export class TakeRecommendationComponent implements OnInit {
    recommendedBook: Book | null = null;
    recommendedPlaylist: { song: string, artist: string, year: number, popularity: number, danceability: number, energy: number, valence: number, tempo: number, genre: string }[] = [];

    constructor(private http: HttpClient, private userService: UserService) { }

    ngOnInit() {
        console.log("TakeRecommendationComponent initialized.");
        this.takeRec();
    }

    takeRec() {
        console.log("Take rec clicked!")
        const username = this.userService.getUsername();

        if (!username) {
            console.error("No username found! Ensure the user is logged in.");
            return;
        }

        console.log("Initiating recommendation request for user:", username);

        this.http.post<RecommendationResponse>('http://localhost:5000/recommend', { username }).subscribe(
            (response) => {
                console.log("Response received:", response);
                if (response.success) {
                    // Create a new book object with match scores
                    this.recommendedBook = {
                        ...response.data.book,
                        match_scores: response.data.match_scores  // Add match scores here
                    };
                    this.recommendedPlaylist = response.data.playlist;
                    console.log("Updated recommendedBook:", this.recommendedBook);
                } else {
                    console.error("Error:", response.message);
                }
            },
            (error) => console.error("API error:", error)
        );
    }
}