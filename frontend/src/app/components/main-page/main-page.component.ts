import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
    selector: 'app-main-page',
    templateUrl: './main-page.component.html',
    styleUrls: ['./main-page.component.css']
})
export class MainPageComponent {

    constructor(private router: Router) { }

    navigateTo(path: string) {
        console.log(`Navigating to: ${path}`);
        this.router.navigate([`/${path}`]);
    }
}
