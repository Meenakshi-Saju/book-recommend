import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router'; // Import this

import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { LoginComponent } from './components/login/login.component';
// import { RegisterComponent } from './components/register/register.component';
import { HomeComponent } from './components/home/home.component';
import { MainPageComponent } from './components/main-page/main-page.component';
import { BookRecommendationComponent } from './components/main-page/book-recommendation/book-recommendation.component';
import { ClockComponent } from './components/clock/clock.component';
import { GiveRecommendationComponent } from './components/main-page/book-recommendation/give-recommendation/give-recommendation.component';
import { TakeRecommendationComponent } from './components/main-page/book-recommendation/take-recommendation/take-recommendation.component';
import { SongRecommendationComponent } from './components/main-page/song-recommendation/song-recommendation.component';
import { WritersSectionComponent } from './components/main-page/writing-section/writers-section.component';
import { ResourcesComponent } from './components/main-page/writing-section/resources/resources.component';
import { WritingPromptComponent } from './components/main-page/writing-section/writing-prompt/writing-prompt.component';
import { WritingBoxComponent } from './components/main-page/writing-section/write/write.component';
import { PodcastsVideosComponent } from './components/main-page/writing-section/resources/podcasts-videos/podcasts-videos.component';
import { BookResourcesComponent } from './components/main-page/writing-section/resources/books-resources/books-resources.component';
import { SearchDetailsComponent } from './components/main-page/book-recommendation/search-details/search-details.component';
import { LoadingComponent } from './components/main-page/book-recommendation/take-recommendation/loading/loading.component';
import { DisplayComponent } from './components/main-page/book-recommendation/take-recommendation/display/display.component';
import { GenresComponent } from './components/genres/genres.component';
@NgModule({
    declarations: [
        AppComponent,
        LoginComponent,
        // RegisterComponent,
        HomeComponent,
        MainPageComponent,
        BookRecommendationComponent,
        ClockComponent,
        GiveRecommendationComponent,
        TakeRecommendationComponent,
        SongRecommendationComponent,
        WritersSectionComponent,
        WritingPromptComponent,
        WritingBoxComponent,
        ResourcesComponent,
        BookResourcesComponent,
        PodcastsVideosComponent,
        SearchDetailsComponent,
        LoadingComponent,
        DisplayComponent,
        GenresComponent

    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        FormsModule,
        CommonModule,
        HttpClientModule
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule { }
