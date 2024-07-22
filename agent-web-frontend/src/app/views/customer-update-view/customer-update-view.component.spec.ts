import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerUpdateViewComponent } from './customer-update-view.component';

describe('CompanyBasicInfoComponent', () => {
  let component: CustomerUpdateViewComponent;
  let fixture: ComponentFixture<CustomerUpdateViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CustomerUpdateViewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomerUpdateViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
