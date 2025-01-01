import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Router } from '@angular/router';

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
    };
}

@Component({
    selector: 'app-display',
    templateUrl: './display.component.html',
    styleUrls: ['./display.component.css']
})
export class DisplayComponent implements OnChanges {
    @Input() recommendedBook: Book | null = null;
    @Input() recommendedPlaylist: { song: string, artist: string, year: number, genre: string }[] = [];

    ngOnChanges(changes: SimpleChanges) {
        if (changes['recommendedBook']) {
            console.log('Recommended Book:', this.recommendedBook);
            console.log('Match Scores:', this.recommendedBook?.match_scores);
        }
    }
}