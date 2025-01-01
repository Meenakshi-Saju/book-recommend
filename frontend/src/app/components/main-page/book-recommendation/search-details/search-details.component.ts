import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-search-details',
    templateUrl: './search-details.component.html',
    styleUrls: ['./search-details.component.css']
})
export class SearchDetailsComponent implements OnInit {
    bookDetails: any;

    constructor(private route: ActivatedRoute) { }

    ngOnInit(): void {
        this.route.queryParams.subscribe(params => {
            this.bookDetails = {
                title: params['title'],
                author: params['author'],
                description: params['description'],
                genre: params['genre'],
                url: params['url']
            };
            console.log("Received bookDetails in search-details component:", this.bookDetails);
        });
    }

}
