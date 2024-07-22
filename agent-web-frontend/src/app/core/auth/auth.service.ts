import {Injectable} from '@angular/core';
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {CookieService} from "ngx-cookie-service";
import {AuthLoginResponse} from "../../services/agent-api-service/agent-api-dto";
import {Observable} from "rxjs";
import {Router} from "@angular/router";
import {environment} from "../../../environments/environment";

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(
    private agentApiService: AgentApiService,
    private cookieService: CookieService,
    private router: Router
  ) {
  }

  login(username: string, password: string): Observable<AuthLoginResponse> {
    return this.agentApiService.loginViewSubmit({username: username, password: password});
  }

  logout() {
    this.cookieService.delete(environment.authCookieName, environment.authCookiePath, environment.authCookieDomain);
  }

  isAuthenticated(): boolean {
    const userCookie = this.cookieService.get(environment.authCookieName)
    return !!userCookie;
  }
}
