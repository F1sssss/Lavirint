import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UiService {
  loader: boolean = false;

  constructor() { }

  loaderOn() {
    this.loader = true;
  }

  loaderOff() {
    this.loader = false;
  }
}
