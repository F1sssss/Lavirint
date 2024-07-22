import { ResolveFn } from '@angular/router';
import {inject} from "@angular/core";
import {DataService} from "../services/data-service/data.service";

export const dataResolver: ResolveFn<any> = (route, state) => {
  return inject(DataService).getData();
};
