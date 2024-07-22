import {Component} from '@angular/core';
import {Router} from "@angular/router";
import {AuthService} from "./core/auth/auth.service";
import {UiService} from "./services/ui-service/ui.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(
    private router: Router,
    protected authService: AuthService,
    protected uiService: UiService
  ) {
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/', 'login']);
  }
}
