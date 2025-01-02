import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { RecommendationService } from '../../../../../services/recommendation.service';
import { UserService } from '../../../../../services/user.service';
interface Book {
    title: string;
    author: string;
    genre: string;
    description: string;
    url: string;
    match_scores?: {
        overall_match: number;
        notes_match: number;
        genre_match: number;
        feedback_match: number;
    };
}

interface FeedbackState {
    liked: boolean;
    saved: boolean;
    shared: boolean;
    clicked: boolean;
}

@Component({
    selector: 'app-display',
    templateUrl: './display.component.html',
    styleUrls: ['./display.component.css']
})
export class DisplayComponent implements OnChanges {
    @Input() recommendedBook: Book | null = null;
    @Input() recommendedPlaylist: { song: string, artist: string, year: number, genre: string }[] = [];
    username: string = '';

    feedbackState: FeedbackState = {
        liked: false,
        saved: false,
        shared: false,
        clicked: false
    };

    constructor(private recommendationService: RecommendationService,
        private userService: UserService
    ) { }
    ngOnChanges(changes: SimpleChanges): void {
        if (changes['recommendedBook'] && this.recommendedBook && this.username) {
            console.log('Book changed, loading feedback');
            this.loadExistingFeedback();
        }
    }

    ngOnInit() {
        // Get initial username
        this.username = this.userService.getUsername() || '';

        // Subscribe to username changes from UserService
        this.userService.getUsernameObservable().subscribe(username => {
            if (this.username !== username) {
                this.username = username;
                this.resetFeedbackState();
                if (this.recommendedBook) {
                    this.loadExistingFeedback();
                }
            }
        });

        if (this.username && this.recommendedBook) {
            this.loadExistingFeedback();
        }
    }





    // ngOnChanges(changes: SimpleChanges) {
    //     if (changes['recommendedBook'] && this.recommendedBook && this.username) {
    //         console.log('Book changed, loading feedback');
    //         this.loadExistingFeedback();
    //     }
    // }

    private resetFeedbackState() {
        this.feedbackState = {
            liked: false,
            saved: false,
            shared: false,
            clicked: false
        };
    }

    // loadExistingFeedback() {
    //     if (!this.username || !this.recommendedBook?.title) {
    //         console.log('Missing username or book title for feedback');
    //         return;
    //     }

    //     console.log(`Loading feedback for user ${this.username} and book ${this.recommendedBook.title}`);

    //     this.recommendationService.getUserFeedback(this.username, this.recommendedBook.title)
    //         .subscribe({
    //             next: (feedback: any) => {
    //                 if (feedback.success && feedback.data) {
    //                     this.feedbackState = feedback.data;
    //                 }
    //             },
    //             error: (error) => console.error('Error loading feedback:', error)
    //         });
    // }

    loadExistingFeedback() {
        if (!this.username || !this.recommendedBook?.title) {
            console.log('Missing username or book title for feedback');
            return;
        }

        console.log(`Loading feedback for user ${this.username} and book ${this.recommendedBook.title}`);

        this.recommendationService.getUserFeedback(this.username, this.recommendedBook.title)
            .subscribe({
                next: (feedback: any) => {
                    if (feedback.success && feedback.data) {
                        this.feedbackState = feedback.data;
                    }
                },
                error: (error) => console.error('Error loading feedback:', error)
            });
    }


    toggleFeedback(type: keyof FeedbackState) {
        if (!this.recommendedBook || !this.username) {
            console.error('Cannot toggle feedback: missing book or username');
            return;
        }

        console.log('Toggling feedback:', type, 'for user:', this.username);

        // Update local state optimistically
        this.feedbackState[type] = !this.feedbackState[type];

        this.recommendationService.submitFeedback(
            this.username,
            this.recommendedBook.title,
            type,
            this.feedbackState[type]
        ).subscribe({
            next: (response) => {
                console.log('Feedback submitted successfully:', response);
                if (type === 'liked' || type === 'saved') {
                    this.recommendationService.triggerNewRecommendation(this.username);
                }
            },
            error: (error) => {
                console.error('Feedback submission failed:', error);
                // Revert on error
                this.feedbackState[type] = !this.feedbackState[type];
                alert('Failed to save feedback. Please try again.');
            }
        });
    }

    shareBook() {
        if (!this.recommendedBook) return;

        const shareText = `Check out "${this.recommendedBook.title}" by ${this.recommendedBook.author} on Goodreads: ${this.recommendedBook.url}`;

        if (navigator.share) {
            navigator.share({
                title: this.recommendedBook.title,
                text: shareText,
                url: this.recommendedBook.url
            })
                .then(() => this.toggleFeedback('shared'))
                .catch(error => {
                    console.error('Error sharing:', error);
                    this.handleShareFallback(shareText);
                });
        } else {
            this.handleShareFallback(shareText);
        }
    }

    private handleShareFallback(shareText: string) {
        navigator.clipboard.writeText(shareText)
            .then(() => {
                alert('Link copied to clipboard!');
                this.toggleFeedback('shared');
            })
            .catch(error => {
                console.error('Error copying to clipboard:', error);
                alert('Unable to share. Please try again.');
            });
    }

}