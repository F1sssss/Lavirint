import { TestBed } from '@angular/core/testing';

import { AgentApiService } from './agent-api.service';

describe('AgentApiService', () => {
  let service: AgentApiService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AgentApiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
