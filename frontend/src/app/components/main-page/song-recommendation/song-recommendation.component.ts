import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RecommendationService } from '../../../services/recommendation.service';


@Component({
    selector: 'app-song-recommendation',
    templateUrl: './song-recommendation.component.html',
    styleUrls: ['./song-recommendation.component.css']
})
export class SongRecommendationComponent {
    bookTitle: string = '';
    playlist: any[] = [];
    errorMessage: string = '';

    constructor(private http: HttpClient, private recommendationService: RecommendationService) { }

    fetchPlaylist() {
        if (!this.bookTitle.trim()) {
            alert("Please enter a book title!");
            this.errorMessage = "Please enter a book title.";
            return;
        }

        this.recommendationService.getPlaylistForBook(this.bookTitle).subscribe(
            (response) => {
                this.playlist = response;
                this.errorMessage = '';
            },
            (error) => {
                this.errorMessage = error.error.message || "An error occurred while fetching the playlist.";
                this.playlist = [];
            }
        );

    }
}
