import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerCertificateExpirationBadgeComponent } from './customer-certificate-expiration-badge.component';

describe('CustomerCertificateExpirationBadgeComponent', () => {
  let component: CustomerCertificateExpirationBadgeComponent;
  let fixture: ComponentFixture<CustomerCertificateExpirationBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerCertificateExpirationBadgeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(CustomerCertificateExpirationBadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
