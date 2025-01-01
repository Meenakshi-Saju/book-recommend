import { Component } from '@angular/core';

@Component({
    selector: 'app-writing-prompt',
    templateUrl: './writing-prompt.component.html',
    styleUrls: ['./writing-prompt.component.css']
})
export class WritingPromptComponent {
    writingContent: string = '';
    prompts = {
        fiction: [
            "Write a story about a world where magic is real but illegal.",
            "Describe a character who discovers they have a hidden power.",
            "Write about a journey to find a lost, mythical city.",
            "Imagine a conversation between a ghost and the person haunting them.",
            "Write a scene where two rivals are forced to work together.",
            "Create a story where the protagonist can time-travel only once.",
            "Write about an inventor whose creation goes terribly wrong.",
            "Describe a place where dreams and reality blend together.",
            "Imagine a world where everyone lives underground.",
            "Write about a character who learns a shocking family secret.",
            "Write about a world where every lie someone tells becomes true.",
            "Imagine a city where everyone has a unique superpower.",
            "Describe a world where time is frozen for everyone but one person.",
            "Write about a conversation between two people from different eras.",
            "Create a story about a person who discovers a hidden magical ability."
        ],
        nonFiction: [
            "Describe a moment that changed your perspective on life.",
            "Write about someone who has greatly influenced you.",
            "What are three values that are most important to you?",
            "Write about a challenging goal you set and achieved.",
            "Describe a meaningful conversation you had recently.",
            "Write about a place that brings you peace and why.",
            "Reflect on a book or movie that inspired you.",
            "Write about a time when you felt out of your comfort zone.",
            "Describe a skill you've worked hard to develop.",
            "Write about a tradition that means a lot to you."
        ]
    };

    generatePrompt(category: 'fiction' | 'nonFiction') {
        const promptArray = this.prompts[category];
        const randomIndex = Math.floor(Math.random() * promptArray.length);
        const promptText = promptArray[randomIndex];
        document.getElementById('prompt')!.textContent = promptText;
    }

    downloadText() {
        const text = this.writingContent;
        const prompt = document.getElementById('prompt')!.textContent;
        const filename = 'Your_Writing.txt';
        const fileContent = `Prompt: ${prompt}\n\nYour Writing:\n${text}`;
        const blob = new Blob([fileContent], { type: 'text/plain' });
        const link = document.createElement('a');

        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();

        URL.revokeObjectURL(link.href); // Clean up the URL object
    }
}
