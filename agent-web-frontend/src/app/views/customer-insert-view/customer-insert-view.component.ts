import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {Router} from "@angular/router";
import {FormBuilder, FormControl, Validators} from "@angular/forms";
import {FisValidators} from "../../core/fisValidators";
import {Location} from "@angular/common";
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";

@Component({
  selector: 'app-company-insert',
  templateUrl: './customer-insert-view.component.html',
  styleUrls: ['./customer-insert-view.component.scss']
})
export class CustomerInsertViewComponent implements OnInit, AfterViewInit {

  @ViewChild('nameInput') nameInput = {} as ElementRef<HTMLInputElement>;

  viewStatus: string = 'idle';

  public formGroup = this.formBuilder.group({
    name: new FormControl<string | null>(null, [Validators.required]),
    identificationNumber: [null, [Validators.required, FisValidators.companyIdentificationNumber ]],
    taxNumber: new FormControl<string | null>(null),
    address: new FormControl<string | null>(null, [Validators.required]),
    city: new FormControl<string | null>(null, [Validators.required]),
    countryId: [39, [Validators.required]],
    isActive: new FormControl<boolean | null>(true, [Validators.required]),
    isTaxpayer: new FormControl<boolean | null>(null, [Validators.required]),
    bankAccount: new FormControl<string | null>(null),
    phoneNumber: new FormControl<string | null>(null),
    emailAddress: new FormControl<string | null>(null),
  });

  constructor(
    public location: Location,
    private router: Router,
    private formBuilder: FormBuilder,
    private agentApiService: AgentApiService
  ) {
  }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.nameInput.nativeElement.focus();
    });
  }

  submit() {
    if (this.formGroup.invalid) {
      return;
    }

    let data = this.formGroup.value;

    this.viewStatus = 'loading';
    this.agentApiService.customerInsertViewSubmit(data).subscribe(response => {
      if (response.errorMessage !== null) {
        this.router.navigate(['company'])
      }
    });
  }
}
