import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor, HttpResponse
} from '@angular/common/http';
import {catchError, map, Observable, of} from 'rxjs';
import {Router} from "@angular/router";

@Injectable()
export class MainInterceptor implements HttpInterceptor {

  constructor(
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      map(resp => {
        return resp;
      }),
      catchError((error) => {
        if (error.status === 401) {
          this.router.navigate(['/login'], { state: {
            errorMessage: "Vaša sesija je istekla. Molimo da se ponovo prijavite." }
          });
        }

        if (error.status === 503) {
          this.router.navigate(['/login'], { state: {
            errorMessage: "Servis trenutno nije dostupan." }
          });
        }

        return of(error);
      })
    );
  }
}
