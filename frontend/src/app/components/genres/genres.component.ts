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
  // Track selected genres and notes
  selectedGenres: string[] = [];
  notes: string = '';

  constructor(private authService: AuthService, private userService: UserService, private router: Router) { this.username = this.userService.getUsername(); }


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

  // constructor(private http: HttpClient) { }

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
    // this.setupCheckboxHandlers();

    // Set up notes handler
    // this.setupNotesHandler();
  }

  onGenreChange(event: any, genre: string) {
    if (event.target.checked) {
      this.selectedGenres.push(genre);
    } else {
      this.selectedGenres = this.selectedGenres.filter(g => g !== genre);
    }
    console.log('Selected genres:', this.selectedGenres);
  }

  savePreferences() {
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

    console.log('Sending data:', data);

    this.authService.saveGenresAndNotes(data).subscribe({
      next: (response) => {
        if (response.success) {
          alert('Preferences saved!');
          this.router.navigate(['/main-page']);
        }
      },
      error: (err) => console.error('Error:', err)
    });
  }
}



