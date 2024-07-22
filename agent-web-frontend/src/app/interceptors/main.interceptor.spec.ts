import { TestBed } from '@angular/core/testing';

import { MainInterceptor } from './main.interceptor';

describe('MainInterceptor', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [
      MainInterceptor
      ]
  }));

  it('should be created', () => {
    const interceptor: MainInterceptor = TestBed.inject(MainInterceptor);
    expect(interceptor).toBeTruthy();
  });
});
