import { Component } from '@angular/core';

@Component({
    selector: 'app-podcasts-videos',
    templateUrl: "./podcasts-videos.component.html",
    styleUrls: ['./podcasts-videos.component.css']
})
export class PodcastsVideosComponent {

    podcasts = [
        {
            title: "Writing Excuses",
            link: "https://writingexcuses.com/",
            description: "A short, insightful podcast featuring professional writers sharing tips on various aspects of writing and storytelling."
        },
        {
            title: "The Well-Storied Podcast",
            link: "https://www.well-storied.com/podcast",
            description: "Covers writing techniques, the publishing industry, and actionable advice for both new and experienced writers."
        },
        {
            title: "Story Grid Podcast",
            link: "https://www.storygrid.com/podcast/",
            description: "Focuses on story structure, genre, and editing, hosted by editor Shawn Coyne and author Tim Grahl."
        },
        {
            title: "The Creative Penn",
            link: "https://www.thecreativepenn.com/podcasts/",
            description: "Hosted by Joanna Penn, this podcast offers advice on creative writing, publishing, and book marketing."
        }
    ];

    videos = [
        {
            title: "Jenna Moreci's Writing Advice",
            link: "https://www.youtube.com/c/JennaMoreci",
            description: "YouTube channel with straightforward advice on writing, editing, and character development."
        },
        {
            title: "Author Level Up",
            link: "https://www.youtube.com/c/AuthorLevelUp",
            description: "Hosted by Michael La Ronn, offering tips on productivity, self-publishing, and growing a writing career."
        },
        {
            title: "Helping Writers Become Authors",
            link: "https://www.youtube.com/c/KMWeiland",
            description: "K.M. Weiland’s video series on story structure, character arcs, and plot development."
        },
        {
            title: "Terrible Writing Advice",
            link: "https://www.youtube.com/user/writerlyvideos",
            description: "A humorous take on writing advice, highlighting common mistakes to avoid, presented by J.P. Beaubien."
        }
    ];
}
