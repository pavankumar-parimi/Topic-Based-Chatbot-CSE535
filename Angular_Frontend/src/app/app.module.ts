// import { NgModule } from '@angular/core';
// import { BrowserModule } from '@angular/platform-browser';

// import { AppRoutingModule } from './app-routing.module';
// import { AppComponent } from './app.component';
// import { ChatComponent } from './chat/chat.component';
// import { FooterComponent } from './footer/footer.component';
// import { HeaderComponent } from './header/header.component';
// import { ChatService } from './chat.service';

// import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown';

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';

import { ChatService } from './chat.service';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown';
import { HttpClientModule } from '@angular/common/http';
import { NgChartsModule } from 'ng2-charts';
 

@NgModule({
  declarations: [
    AppComponent,
    FooterComponent,
    HeaderComponent
  ],
  imports: [
    // BrowserModule,
    // AppRoutingModule,
    // NgMultiSelectDropDownModule.forRoot()
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    BrowserAnimationsModule,
    NgMultiSelectDropDownModule.forRoot(),
    HttpClientModule,
    NgChartsModule.forRoot()
  ],
  providers: [ChatService],
  bootstrap: [AppComponent]
})
export class AppModule { }
