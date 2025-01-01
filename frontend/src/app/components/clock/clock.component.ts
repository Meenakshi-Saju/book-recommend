import { Component, OnInit } from '@angular/core';

@Component({
    selector: 'app-clock',
    templateUrl: './clock.component.html',
    styleUrls: ['./clock.component.css']
})
export class ClockComponent implements OnInit {

    ngOnInit(): void {
        this.updateClock();
        setInterval(this.updateClock, 1000);
    }

    updateClock(): void {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        const seconds = now.getSeconds();

        const hourDeg = (hours % 12) * 30 + (minutes / 2); // 30 degrees per hour + fraction based on minutes
        const minuteDeg = minutes * 6; // 6 degrees per minute
        const secondDeg = seconds * 6; // 6 degrees per second

        document.getElementById('hour')!.style.transform = `translateX(-50%) rotate(${hourDeg}deg)`;
        document.getElementById('minute')!.style.transform = `translateX(-50%) rotate(${minuteDeg}deg)`;
        document.getElementById('second')!.style.transform = `translateX(-50%) rotate(${secondDeg}deg)`;
    }
}
