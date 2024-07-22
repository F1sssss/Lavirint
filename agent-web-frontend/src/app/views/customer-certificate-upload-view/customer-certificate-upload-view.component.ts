import { Component } from '@angular/core';
import {ActivatedRoute, Router, RouterLink} from "@angular/router";
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {delay} from "rxjs";
import {AsyncPipe, NgClass} from "@angular/common";
import {FormBuilder, FormControl, ReactiveFormsModule, Validators} from "@angular/forms";

class ChangeEvent<T> {
}

@Component({
  selector: 'app-customer-certificate-upload-view',
  standalone: true,
  imports: [
    RouterLink,
    AsyncPipe,
    ReactiveFormsModule,
    NgClass
  ],
  templateUrl: './customer-certificate-upload-view.component.html',
  styleUrl: './customer-certificate-upload-view.component.scss'
})
export class CustomerCertificateUploadViewComponent {
  customer!: any;
  loader = false;

  protected formGroup = this.formBuilder.group({
    certificate: new FormControl<File | null>(null, [Validators.required]),
    password: new FormControl(null, [Validators.required])
  });

  constructor(
    private apiService: AgentApiService,
    private route: ActivatedRoute,
    private formBuilder: FormBuilder,
    private router: Router
  ) {
    this.loader = true;
    this.route.paramMap.subscribe(params => {
      this.apiService.customerCertificateUploadViewLoad({
        customerId: params.get('customerId')
      }).pipe(
        delay(600)
      ).subscribe(response => {
        this.loader = false;
        this.customer = response.customer;
      })
    });
  }

  onCertificateSelect($event: Event) {
    const target = $event.target as HTMLInputElement;
    if (target.files !== null && target.files.length > 0) {
      this.formGroup.patchValue({ certificate: target.files![0] })
    } else {
      this.formGroup.patchValue({ certificate: null })
    }
  }

  submit() {
    if (this.formGroup.invalid) {
      return;
    }

    const formData = this.formGroup.value;

    const httpFormData = new FormData();
    httpFormData.set('customerId', this.customer.id);
    httpFormData.set('certificate', formData.certificate!);
    httpFormData.set('password', formData.password!);

    this.apiService.customerCertificateUploadViewSubmit(httpFormData).subscribe(response => {
      if (response.error) {
        this.formGroup.setErrors({ server: response.error });
      } else {
        this.router.navigate(['/', 'customer', this.customer.id, 'certificates', 'view'])
      }
    });
  }
}
