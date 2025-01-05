import { Component, OnInit, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router'; // Import the Router

@Component({
    selector: 'app-main-page',
    templateUrl: './main-page.component.html',
    styleUrls: ['./main-page.component.css']
})
export class MainPageComponent implements OnInit, AfterViewInit {
    canvas: HTMLCanvasElement;
    ctx: CanvasRenderingContext2D | null;

    constructor(private router: Router) {  // Inject Router into the constructor
        this.canvas = document.createElement('canvas') as HTMLCanvasElement;
        this.ctx = null;
    }

    ngOnInit(): void { }

    ngAfterViewInit(): void {
        this.canvas = document.getElementById('game') as HTMLCanvasElement;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.ctx = this.canvas.getContext('2d');

        // Ensure no scrollbars
        document.documentElement.style.overflow = 'hidden';
        document.body.style.overflow = 'hidden';

        // Redraw the canvas when window is resized
        window.addEventListener('resize', this.handleResize);

        if (this.ctx) {
            this.generateTrees();
            this.drawBackground();
        }
    }

    ngOnDestroy(): void {
        // Clean up event listener when component is destroyed
        window.removeEventListener('resize', this.handleResize);
    }

    handleResize = () => {
        // Resize the canvas on window resize
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.drawBackground();
    }

    // Method for navigation
    navigateTo(page: string) {
        this.router.navigate([page]); // Navigate to the specified route
    }

    hill1BaseHeight = 100;
    hill1Amplitude = 10;
    hill1Stretch = 1;
    hill2BaseHeight = 70;
    hill2Amplitude = 20;
    hill2Stretch = 0.5;

    trees: Array<{ x: number, color: string }> = [];

    generateTrees() {
        const minimumGap = 30;
        const maximumGap = 150;
        const treeColors = ['#6D8821', '#8FAC34', '#98B333'];

        let lastX = 0;
        while (lastX < window.innerWidth) {
            const x = lastX + minimumGap + Math.random() * (maximumGap - minimumGap);
            const color = treeColors[Math.floor(Math.random() * treeColors.length)];
            this.trees.push({ x, color });
            lastX = x;
        }
    }

    drawBackground() {
        const ctx = this.ctx;
        if (ctx) {
            const gradient = ctx.createLinearGradient(0, 0, 0, window.innerHeight);
            gradient.addColorStop(0, '#BBD691');
            gradient.addColorStop(1, '#FEF1E1');
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

            this.drawHill(this.hill1BaseHeight, this.hill1Amplitude, this.hill1Stretch, '#95C629');
            this.drawHill(this.hill2BaseHeight, this.hill2Amplitude, this.hill2Stretch, '#659F1C');

            this.trees.forEach((tree) => this.drawTree(tree.x, tree.color));
        }
    }

    drawHill(baseHeight: number, amplitude: number, stretch: number, color: string) {
        const ctx = this.ctx;
        if (ctx) {
            ctx.beginPath();
            ctx.moveTo(0, window.innerHeight);
            ctx.lineTo(0, this.getHillY(0, baseHeight, amplitude, stretch));
            for (let i = 0; i < window.innerWidth; i++) {
                ctx.lineTo(i, this.getHillY(i, baseHeight, amplitude, stretch));
            }
            ctx.lineTo(window.innerWidth, window.innerHeight);
            ctx.fillStyle = color;
            ctx.fill();
        }
    }

    drawTree(x: number, color: string) {
        const ctx = this.ctx;
        if (ctx) {
            ctx.save();
            ctx.translate(x * this.hill1Stretch, this.getTreeY(x, this.hill1BaseHeight, this.hill1Amplitude));

            const trunkHeight = 5;
            const trunkWidth = 2;
            const crownHeight = 25;
            const crownWidth = 10;

            ctx.fillStyle = '#7D833C';
            ctx.fillRect(-trunkWidth / 2, -trunkHeight, trunkWidth, trunkHeight);

            ctx.beginPath();
            ctx.moveTo(-crownWidth / 2, -trunkHeight);
            ctx.lineTo(0, -(trunkHeight + crownHeight));
            ctx.lineTo(crownWidth / 2, -trunkHeight);
            ctx.fillStyle = color;
            ctx.fill();

            ctx.restore();
        }
    }

    getHillY(windowX: number, baseHeight: number, amplitude: number, stretch: number) {
        const sineBaseY = window.innerHeight - baseHeight;
        return Math.sin((windowX * stretch * Math.PI) / 180) * amplitude + sineBaseY;
    }

    getTreeY(x: number, baseHeight: number, amplitude: number) {
        const sineBaseY = window.innerHeight - baseHeight;
        return Math.sin((x * Math.PI) / 180) * amplitude + sineBaseY;
    }
}
