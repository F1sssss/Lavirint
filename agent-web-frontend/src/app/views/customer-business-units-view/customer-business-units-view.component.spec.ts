import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerBusinessUnitsViewComponent } from './customer-business-units-view.component';

describe('CustomerOrganizationalUnitsListViewComponent', () => {
  let component: CustomerBusinessUnitsViewComponent;
  let fixture: ComponentFixture<CustomerBusinessUnitsViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CustomerBusinessUnitsViewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomerBusinessUnitsViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
