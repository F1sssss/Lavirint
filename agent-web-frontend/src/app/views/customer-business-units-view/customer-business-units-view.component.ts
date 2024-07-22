import { Component } from '@angular/core';
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {ActivatedRoute, RouterLink} from "@angular/router";

@Component({
  selector: 'app-customer-organizational-units-list-view',
  standalone: true,
  imports: [
    RouterLink
  ],
  templateUrl: './customer-business-units-view.component.html',
  styleUrl: './customer-business-units-view.component.scss'
})
export class CustomerBusinessUnitsViewComponent {
  customer!: any;
  organizationalUnits!: any[];
  constructor(
    apiService: AgentApiService,
    route: ActivatedRoute
  ) {
    route.paramMap.subscribe(params => {
      apiService.customerBusinessUnitsListViewLoad({
        customerId: params.get('customerId')
      }).subscribe(response => {
        this.customer = response.customer;
        this.organizationalUnits = response.organizationalUnits;
      });
    })
  }
}
