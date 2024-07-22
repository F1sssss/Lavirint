import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {RouterModule} from "@angular/router";
import {routes} from "./app.routing";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MainInterceptor} from "./interceptors/main.interceptor";
import {CommonModule} from "@angular/common";
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ConfirmModalComponent } from './modals/confirm-modal/confirm-modal.component';
import {LoginViewComponent} from "./views/login-view/login-view.component";
import {CustomerListViewComponent} from "./views/customer-list-view/customer-list-view.component";
import {CustomerInsertViewComponent} from "./views/customer-insert-view/customer-insert-view.component";
import {CustomerUpdateViewComponent} from "./views/customer-update-view/customer-update-view.component";
import {
  CustomerCertificateExpirationBadgeComponent
} from "./components/customer-certificate-expiration-badge/customer-certificate-expiration-badge.component";


@NgModule({
  declarations: [
    AppComponent,
    CustomerListViewComponent,
    CustomerUpdateViewComponent,
    LoginViewComponent,
    CustomerInsertViewComponent,
    ConfirmModalComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule,
    NgbModule,
    CustomerCertificateExpirationBadgeComponent
  ],
  exports: [
    RouterModule
  ],
  providers: [
    {provide: HTTP_INTERCEPTORS, useClass: MainInterceptor, multi: true}
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
