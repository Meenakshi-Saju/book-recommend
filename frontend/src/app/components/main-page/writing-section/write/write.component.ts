import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
    selector: 'app-writing-box',
    templateUrl: './write.component.html',
    styleUrls: ['./write.component.css']
})
export class WritingBoxComponent {

    prompt: string = '';

    downloadText(): void {
        const nameInput = document.getElementById("name") as HTMLTextAreaElement;
        const writingArea = document.getElementById("writingArea") as HTMLTextAreaElement;

        const text = writingArea.value;
        const name = nameInput.value.trim() || "Untitled";
        const filename = `${name}.txt`;
        const fileContent = `Your Writing:\n\n${text}`;
        const blob = new Blob([fileContent], { type: "text/plain" });
        const link = document.createElement("a");

        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();

        URL.revokeObjectURL(link.href);
    }
}
