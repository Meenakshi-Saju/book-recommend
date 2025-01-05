import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

interface PreferencesData {
  username: string;
  genres: string[];
  notes: string;
}



@Component({
  selector: 'app-genres',
  templateUrl: './genres.component.html',
  styleUrls: ['./genres.component.scss']
})

export class GenresComponent implements OnInit {
  selectedGenres: string[] = [];
  notes: string = '';
  username: string;

  availableGenres = [
    'Fiction',
    'Non Fiction',
    'Classics',
    'Fantasy',
    'Romance',
    'Young Adult'
  ];

  constructor(
    private authService: AuthService,
    private userService: UserService,
    private router: Router
  ) {
    this.username = this.userService.getUsername();
  }

  ngOnInit() {
    // Fetch existing preferences when component loads
    this.fetchUserPreferences();
    this.setupModalHandlers();
  }

  private fetchUserPreferences() {
    const username = this.userService.getUsername();
    if (username) {
      // Add this method to your AuthService
      this.authService.getUserPreferences(username).subscribe({
        next: (response: any) => {
          if (response.success) {
            this.selectedGenres = response.data.genres || [];
            this.notes = response.data.notes || '';
            // Update checkboxes
            this.updateCheckboxes();
          }
        },
        error: (err) => console.error('Error fetching preferences:', err)
      });
    }
  }

  private updateCheckboxes() {
    // Update checkbox states based on selectedGenres
    this.availableGenres.forEach(genre => {
      const checkbox = document.querySelector(`input[value="${genre}"]`) as HTMLInputElement;
      if (checkbox) {
        checkbox.checked = this.selectedGenres.includes(genre);
      }
    });
  }

  private setupModalHandlers() {
    const genreText = document.getElementById('genreText');
    const genreModal = document.getElementById('genreModal')!;
    const notesModal = document.getElementById('notesModal')!;
    const closeGenreModal = document.getElementById('closeGenreModal')!;
    const closeNotesModal = document.getElementById('closeNotesModal')!;

    genreText?.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (target.id === 'genre') {
        genreModal.style.display = 'flex';
      } else if (target.id === 'notes') {
        notesModal.style.display = 'flex';
      }
    });

    closeGenreModal.addEventListener('click', () => {
      genreModal.style.display = 'none';
    });

    closeNotesModal.addEventListener('click', () => {
      notesModal.style.display = 'none';
    });
  }

  onGenreChange(event: any, genre: string) {
    if (event.target.checked) {
      this.selectedGenres.push(genre);
    } else {
      this.selectedGenres = this.selectedGenres.filter(g => g !== genre);
    }
  }

  savePreferences(modalType: 'genres' | 'notes') {
    const username = this.userService.getUsername();
    if (!username) {
      alert('Please log in first');
      return;
    }

    const data = {
      username,
      genres: this.selectedGenres,
      notes: this.notes
    };

    this.authService.saveGenresAndNotes(data).subscribe({
      next: (response) => {
        if (response.success) {
          alert('Preferences saved!');
          // Close only the current modal
          const modal = document.getElementById(modalType === 'genres' ? 'genreModal' : 'notesModal');
          if (modal) {
            modal.style.display = 'none';
          }
        }
      },
      error: (err) => console.error('Error:', err)
    });
  }
}