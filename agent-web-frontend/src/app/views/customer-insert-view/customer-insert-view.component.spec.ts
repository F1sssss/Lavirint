import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomerInsertViewComponent } from './customer-insert-view.component';

describe('InsertCompanyComponent', () => {
  let component: CustomerInsertViewComponent;
  let fixture: ComponentFixture<CustomerInsertViewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CustomerInsertViewComponent]
    });
    fixture = TestBed.createComponent(CustomerInsertViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
