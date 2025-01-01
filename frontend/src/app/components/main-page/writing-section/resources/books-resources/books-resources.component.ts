import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-book-resources',
    templateUrl: './books-resources.component.html',
    styleUrls: ['./books-resources.component.css']
})


export class BookResourcesComponent {

    selectedBook: { "Book Name": string; "Goodreads Link": string } | null = null;

    books = [
        {
            "Book Name": "How to Promote Your Self-Published Kindle Books for Free (On Writing and Self-Publishing a Book, #1)",
            "Goodreads Link": "https://www.goodreads.com/book/show/36367410-how-to-promote-your-self-published-kindle-books-for-free?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=1"
        },
        {
            "Book Name": "Figuring the Word: Essays on Books, Writing and Visual Poetics",
            "Goodreads Link": "https://www.goodreads.com/book/show/570506.Figuring_the_Word?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=2"
        },
        {
            "Book Name": "Writing Performance Reviews: A Write It Well Guide (The Write It Well Series of Books on Business Writing)",
            "Goodreads Link": "https://www.goodreads.com/book/show/18954837-writing-performance-reviews?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=3"
        },
        {
            "Book Name": "Second Sight: An Editor's Talks on Writing, Revising, and Publishing Books for Children and Young Adults",
            "Goodreads Link": "https://www.goodreads.com/book/show/10465738-second-sight?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=4"
        },
        {
            "Book Name": "Essential Grammar: A Write It Well Guide (The Write It Well Series of Books on Business Writing)",
            "Goodreads Link": "https://www.goodreads.com/book/show/20925707-essential-grammar?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=5"
        },
        {
            "Book Name": "It's Alive: Bringing Your Nightmares to Life (The Dream Weaver Books on Writing Fiction)",
            "Goodreads Link": "https://www.goodreads.com/book/show/43361482-it-s-alive?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=6"
        },
        {
            "Book Name": "Reform or Revolution & Other Writings (Books on History, Political & Social Science)",
            "Goodreads Link": "https://www.goodreads.com/book/show/168057.Reform_or_Revolution_Other_Writings?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=7"
        },
        {
            "Book Name": "Writing Picture Books: A Hands-On Guide from Story Creation to Publication",
            "Goodreads Link": "https://www.goodreads.com/book/show/6222756-writing-picture-books?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=8"
        },
        {
            "Book Name": "Wild About Books: Essays on Books and Writing",
            "Goodreads Link": "https://www.goodreads.com/book/show/51043458-wild-about-books?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=9"
        },
        {
            "Book Name": "The Essential Books on Writing Boxed Set: 5,000 Writing Prompts, Master Lists for Writers, and Blank Page to Final Draft",
            "Goodreads Link": "https://www.goodreads.com/book/show/63070974-the-essential-books-on-writing-boxed-set?from_search=true&from_srp=true&qid=7NA5yMge2Q&rank=10"
        }
    ];

    // selectedBook: { "Book Name": string; "Goodreads Link": string } | null = null;

    getRandomBook(): void {
        console.log("Clicked!")
        const randomIndex = Math.floor(Math.random() * this.books.length);
        this.selectedBook = this.books[randomIndex];
    }
}
