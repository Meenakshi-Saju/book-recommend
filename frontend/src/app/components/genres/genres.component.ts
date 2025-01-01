import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface GenreData {
  genres: string[];
  notes: string;
}

@Component({
  selector: 'app-genres',
  templateUrl: './genres.component.html',
  styleUrls: ['./genres.component.scss']
})
export class GenresComponent implements OnInit {
  // Track selected genres and notes
  selectedGenres: string[] = [];
  notesText: string = '';

  // List of available genres
  availableGenres = [
    'Fiction',
    'Non Fiction',
    'Classics',
    'Fantasy',
    'Romance',
    'Young Adult'
  ];
  username: any;

  constructor(private http: HttpClient) { }

  ngOnInit() {
    // Modal elements
    const genreText = document.getElementById('genreText');
    const genreModal = document.getElementById('genreModal')!;
    const closeGenreModal = document.getElementById('closeGenreModal')!;
    const notesModal = document.getElementById('notesModal')!;
    const closeNotesModal = document.getElementById('closeNotesModal')!;

    // Genre click handler
    genreText?.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (target.id === 'genre') {
        genreModal.style.display = 'flex';
      } else if (target.id === 'notes') {
        notesModal.style.display = 'flex';
      }
    });

    // Close button handlers
    closeGenreModal?.addEventListener('click', () => {
      genreModal.style.display = 'none';
    });

    closeNotesModal?.addEventListener('click', () => {
      notesModal.style.display = 'none';
    });

    // Close on outside click
    window.addEventListener('click', (e) => {
      if (e.target === genreModal) {
        genreModal.style.display = 'none';
      }
      if (e.target === notesModal) {
        notesModal.style.display = 'none';
      }
    });

    // Set up checkbox handlers
    this.setupCheckboxHandlers();

    // Set up notes handler
    this.setupNotesHandler();
  }

  private setupCheckboxHandlers(): void {
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]');
    checkboxes.forEach((checkbox: Element) => {
      (checkbox as HTMLInputElement).addEventListener('change', (e) => {
        const target = e.target as HTMLInputElement;
        if (target.checked) {
          this.selectedGenres.push(target.parentElement?.textContent?.trim() || '');
        } else {
          const genre = target.parentElement?.textContent?.trim() || '';
          this.selectedGenres = this.selectedGenres.filter(g => g !== genre);
        }
      });
    });
  }

  private setupNotesHandler(): void {
    const notesTextarea = document.getElementById('notesText') as HTMLTextAreaElement;
    notesTextarea?.addEventListener('input', (e) => {
      const target = e.target as HTMLTextAreaElement;
      this.notesText = target.value;
    });
  }

  submitData(): void {
    const data = {
      username: this.username,  // Use the actual logged-in username here
      genres: this.selectedGenres,
      notes: this.notesText
    };

    this.http.post('http://localhost:5000/update-genres-notes', data)
      .subscribe({
        next: (response) => {
          console.log('Genres and notes updated successfully:', response);
          alert('Your preferences have been saved!');
        },
        error: (error) => {
          console.error('Error updating genres and notes:', error);
          alert('Failed to save your preferences. Please try again.');
        }
      });
  }


}