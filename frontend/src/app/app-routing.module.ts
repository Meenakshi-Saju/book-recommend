import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { LoginComponent } from './components/login/login.component';
// import { RegisterComponent } from './components/register/register.component';
import { HomeComponent } from './components/home/home.component';
import { FormsModule } from '@angular/forms';
import { MainPageComponent } from './components/main-page/main-page.component';
import { BookRecommendationComponent } from './components/main-page/book-recommendation/book-recommendation.component';
import { TakeRecommendationComponent } from './components/main-page/book-recommendation/take-recommendation/take-recommendation.component';
import { GiveRecommendationComponent } from './components/main-page/book-recommendation/give-recommendation/give-recommendation.component';
import { SongRecommendationComponent } from './components/main-page/song-recommendation/song-recommendation.component';
import { WritersSectionComponent } from './components/main-page/writing-section/writers-section.component';
import { ResourcesComponent } from './components/main-page/writing-section/resources/resources.component';
import { WritingPromptComponent } from './components/main-page/writing-section/writing-prompt/writing-prompt.component';
import { WritingBoxComponent } from './components/main-page/writing-section/write/write.component';
import { BookResourcesComponent } from './components/main-page/writing-section/resources/books-resources/books-resources.component';
import { PodcastsVideosComponent } from './components/main-page/writing-section/resources/podcasts-videos/podcasts-videos.component';
import { SearchDetailsComponent } from './components/main-page/book-recommendation/search-details/search-details.component';
import { GenresComponent } from './components/genres/genres.component';
export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    // { path: 'register', component: RegisterComponent },
    { path: 'home', component: HomeComponent },
    { path: 'main-page', component: MainPageComponent },
    { path: 'book-recommendation', component: BookRecommendationComponent },
    { path: 'take-recommendation', component: TakeRecommendationComponent },
    { path: 'give-recommendation', component: GiveRecommendationComponent },
    { path: 'song-recommendation', component: SongRecommendationComponent },
    { path: 'writing-section', component: WritersSectionComponent },
    { path: 'writing-prompt', component: WritingPromptComponent },
    { path: 'write', component: WritingBoxComponent },
    { path: 'resources', component: ResourcesComponent },
    { path: 'books-resources', component: BookResourcesComponent },
    { path: 'podcasts-videos', component: PodcastsVideosComponent },
    { path: 'search-details', component: SearchDetailsComponent },
    { path: 'genres', component: GenresComponent }



];


@NgModule({
    imports: [RouterModule.forRoot(routes), CommonModule],
    exports: [RouterModule]
})
export class AppRoutingModule { }
