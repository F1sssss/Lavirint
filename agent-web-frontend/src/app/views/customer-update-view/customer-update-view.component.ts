import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {Location} from '@angular/common';
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {CountryData} from "../../models/CompanyData";
import {CompanyParamIdGeneralInfoOnLoadResponse} from "../../services/agent-api-service/agent-api-dto";
import {FormBuilder, Validators} from "@angular/forms";
import {ActivatedRoute, ParamMap, Router} from "@angular/router";
import {DataService} from "../../services/data-service/data.service";
import {FisValidators} from "../../core/fisValidators";
import {delay, finalize} from "rxjs";

@Component({
  selector: 'app-company-update',
  templateUrl: './customer-update-view.component.html',
  styleUrls: ['./customer-update-view.component.scss']
})
export class CustomerUpdateViewComponent implements OnInit {

  viewStatus: string = 'idle';

  countries: CountryData[] = [];
  filteredCountries: CountryData[] = [];

  formGroup = this.fb.group({
    id: [0, Validators.required],
    name: ['', Validators.required],
    identificationNumber: ['', [Validators.required, FisValidators.companyIdentificationNumber]],
    taxNumber: [''],
    address: ['', Validators.required],
    city: ['', Validators.required],
    isActive: [true, Validators.required],
    isTaxpayer: [true, Validators.required],
    bankAccount: [''],
    phoneNumber: [''],
    emailAddress: ['', Validators.email],
    countryId: [39, Validators.required],
  });

  constructor(
    public location: Location,
    private agentApiService: AgentApiService,
    private route: ActivatedRoute,
    private dataService: DataService,
    private fb: FormBuilder,
    private router: Router
  ) {
  }

  ngOnInit(): void {
    this.route.paramMap.subscribe((paramMap: ParamMap) => {
      this.agentApiService.customerUpdateViewLoad({
        companyId: Number(paramMap.get('id'))
      }).subscribe((response: CompanyParamIdGeneralInfoOnLoadResponse) => {
        this.formGroup.patchValue(response.company);
      });
    });

    this.dataService.getData().subscribe(data => {
      this.countries = data.countries;
    });
  }

  submit() {
    if (this.formGroup.invalid) {
      return;
    }

    let data = this.formGroup.value;

    this.viewStatus = 'loading';
    this.agentApiService.customerUpdateViewSubmit(data)
      .pipe(
        delay(600),
        finalize(() => {
          this.viewStatus = 'idle';
        })
      )
      .subscribe((response) => {
        if (response.errorMessage === null) {
          this.router.navigate(['/', 'customer-list-view']);
        }
      });
  }
}
