import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerCertificateUploadViewComponent } from './customer-certificate-upload-view.component';

describe('CustomerCertificateUploadViewComponent', () => {
  let component: CustomerCertificateUploadViewComponent;
  let fixture: ComponentFixture<CustomerCertificateUploadViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerCertificateUploadViewComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(CustomerCertificateUploadViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
