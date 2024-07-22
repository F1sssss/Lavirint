import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerCertificatesViewComponent } from './customer-certificates-view.component';

describe('CustomerCertificatesViewComponent', () => {
  let component: CustomerCertificatesViewComponent;
  let fixture: ComponentFixture<CustomerCertificatesViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerCertificatesViewComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(CustomerCertificatesViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
