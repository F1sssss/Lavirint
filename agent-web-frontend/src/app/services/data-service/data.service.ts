import {Injectable} from '@angular/core';
import {Observable, of, tap} from "rxjs";
import {AgentApiService} from "../agent-api-service/agent-api.service";
import {COUNTRIES_CONCRETE} from "./static-data/countries";
import {INVOICE_TYPES_CONCRETE} from "./static-data/invoice-type";
import {TAX_RATE_CONCRETE} from "./static-data/tax-rates";

@Injectable({
  providedIn: 'root'
})
export class DataService {

  private staticData: any;

  private countries = COUNTRIES_CONCRETE;
  private invoiceTypes = INVOICE_TYPES_CONCRETE;
  private taxRates = TAX_RATE_CONCRETE;

  constructor(
    private agentApiService: AgentApiService
  ) {

  }

  getData(): Observable<any> {
    if (this.staticData) {
      return of(this.staticData);
    } else {
      return this.agentApiService.dataServiceLoad({}).pipe(
        tap(data => {
          this.staticData = data;
        })
      )
    }
  }
}
