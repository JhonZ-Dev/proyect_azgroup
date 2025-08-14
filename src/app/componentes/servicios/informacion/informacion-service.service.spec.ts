import { TestBed } from '@angular/core/testing';

import { InformacionServiceService } from './informacion-service.service';

describe('InformacionServiceService', () => {
  let service: InformacionServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(InformacionServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
