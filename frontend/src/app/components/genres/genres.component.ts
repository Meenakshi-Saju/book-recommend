import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../../services/user.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

interface PreferencesData {
  username: string;
  genres: string[];
  notes: string;
  age?: number;
  hobbies: string[]; // Add hobbies property
}

@Component({
  selector: 'app-genres',
  templateUrl: './genres.component.html',
  styleUrls: ['./genres.component.scss']
})

export class GenresComponent implements OnInit {
  selectedGenres: string[] = [];
  selectedHobbies: string[] = []; // Add selectedHobbies array
  notes: string = '';
  age: number | null = null;
  username: string;

  availableGenres = [
    'Fiction',
    'Non Fiction',
    'Classics',
    'Fantasy',
    'Romance',
    'Young Adult'
  ];

  availableHobbies = [
    'Reading',
    'Sports',
    'Music',
    'Gaming',
    'Travel',
    'Cooking',
    'Art',
    'Outdoor Activities'
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
            this.age = response.data.age || null;
            this.selectedHobbies = response.data.hobbies || []; // Get hobbies from response
            // Update checkboxes
            this.updateCheckboxes();
          }
        },
        error: (err) => console.error('Error fetching preferences:', err)
      });
    }
  }

  private updateCheckboxes() {
    // Update genre checkboxes
    this.availableGenres.forEach(genre => {
      const checkbox = document.querySelector(`input[value="${genre}"]`) as HTMLInputElement;
      if (checkbox) {
        checkbox.checked = this.selectedGenres.includes(genre);
      }
    });

    // Update hobby checkboxes
    this.availableHobbies.forEach(hobby => {
      const checkbox = document.querySelector(`input[value="${hobby}"]`) as HTMLInputElement;
      if (checkbox) {
        checkbox.checked = this.selectedHobbies.includes(hobby);
      }
    });
  }

  private setupModalHandlers() {
    const genreModal = document.getElementById('genreModal')!;
    const notesModal = document.getElementById('notesModal')!;
    const ageModal = document.getElementById('ageModal')!;
    const hobbiesModal = document.getElementById('hobbiesModal')!; // Add hobbies modal

    const closeGenreModal = document.getElementById('closeGenreModal')!;
    const closeNotesModal = document.getElementById('closeNotesModal')!;
    const closeAgeModal = document.getElementById('closeAgeModal')!;
    const closeHobbiesModal = document.getElementById('closeHobbiesModal')!; // Add close hobbies modal

    // Set up click handlers for all elements
    document.getElementById('genre')?.addEventListener('click', () => {
      genreModal.style.display = 'flex';
    });

    document.getElementById('notes')?.addEventListener('click', () => {
      notesModal.style.display = 'flex';
    });

    document.getElementById('age')?.addEventListener('click', () => {
      ageModal.style.display = 'flex';
    });

    document.getElementById('hobbies')?.addEventListener('click', () => {
      hobbiesModal.style.display = 'flex';
    });

    // Set up close handlers
    closeGenreModal.addEventListener('click', () => {
      genreModal.style.display = 'none';
    });

    closeNotesModal.addEventListener('click', () => {
      notesModal.style.display = 'none';
    });

    closeAgeModal.addEventListener('click', () => {
      ageModal.style.display = 'none';
    });

    closeHobbiesModal.addEventListener('click', () => {
      hobbiesModal.style.display = 'none';
    });
  }

  onGenreChange(event: any, genre: string) {
    if (event.target.checked) {
      this.selectedGenres.push(genre);
    } else {
      this.selectedGenres = this.selectedGenres.filter(g => g !== genre);
    }
  }

  onHobbyChange(event: any, hobby: string) {
    if (event.target.checked) {
      this.selectedHobbies.push(hobby);
    } else {
      this.selectedHobbies = this.selectedHobbies.filter(h => h !== hobby);
    }
  }

  savePreferences(modalType: 'genres' | 'notes' | 'age' | 'hobbies') {
    const username = this.userService.getUsername();
    if (!username) {
      alert('Please log in first');
      return;
    }

    const data = {
      username,
      genres: this.selectedGenres,
      notes: this.notes,
      age: this.age,
      hobbies: this.selectedHobbies // Include hobbies in the data
    };

    this.authService.saveGenresAndNotes(data).subscribe({
      next: (response) => {
        if (response.success) {
          alert('Preferences saved!');
          // Close only the current modal
          const modal = document.getElementById(
            modalType === 'genres' ? 'genreModal' :
              modalType === 'notes' ? 'notesModal' :
                modalType === 'age' ? 'ageModal' : 'hobbiesModal'
          );
          if (modal) {
            modal.style.display = 'none';
          }
        }
      },
      error: (err) => console.error('Error:', err)
    });
  }
}