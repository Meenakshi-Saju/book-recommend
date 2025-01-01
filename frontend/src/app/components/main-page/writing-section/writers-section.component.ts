import { Component } from '@angular/core';

@Component({
    selector: 'app-writers-section',
    templateUrl: './writers-section.component.html',
    styleUrls: ['./writers-section.component.css']
})
export class WritersSectionComponent {
    currentAuthorIndex = 0;
    dailyTip = "Writing is rewriting. Don’t be afraid to make changes to your work.";
    modalOpen = false;

    authors = [
        {
            name: "J.K. Rowling",
            image: "https://cdn.britannica.com/36/235336-050-D26FAD80/J-K-Rowling-2017-Harry-Potter-author.jpg",
            story: "J.K. Rowling went from being a single mother on welfare to the world's best-selling author",
            link: "https://www.mbebooks.com/blog/j-k-rowlings-journey-to-success/"
        },
        {
            name: "George R.R. Martin",
            image: "https://www.easons.com/globalassets/author-pages/george-r-r-martin/george-r-r-martin2.jpg",
            story: "George R.R. Martin took years to write 'A Game of Thrones' and changed the fantasy genre forever",
            link: "http://creativegenius101.blogspot.com/2013/05/game-of-thrones-writing-success.html#:~:text=In%201970%2C%20at%20the%20age,began%20selling%20his%20stories%20professionally."
        },
        {
            name: "Margaret Atwood",
            image: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT29iVSxnG_jvn99RMxRlVvSBcs64hENF8U1w&s",
            story: "Margaret Atwood's 'The Handmaid's Tale' became an iconic work that explored the dystopian future",
            link: "https://www.womenofinfluence.ca/2012/09/10/margaret-atwood-success-story/"
        }
    ];


    get currentAuthor() {
        return this.authors[this.currentAuthorIndex];
    }

    openModal() { this.modalOpen = true; }
    closeModal() { this.modalOpen = false; }

    showAuthor(direction: string) {
        if (direction === 'next') {
            this.currentAuthorIndex = (this.currentAuthorIndex + 1) % this.authors.length;
        } else {
            this.currentAuthorIndex = (this.currentAuthorIndex - 1 + this.authors.length) % this.authors.length;
        }
    }

    generateDailyTip() {
        const tips = [
            "Set small, achievable goals to keep yourself motivated.",
            "Focus on showing, not telling. Let the reader experience the story.",
            "Experiment with different styles and genres to find your voice.",
            "Take breaks while writing; fresh perspectives can spark creativity."
        ];
        this.dailyTip = tips[Math.floor(Math.random() * tips.length)];
    }
}
