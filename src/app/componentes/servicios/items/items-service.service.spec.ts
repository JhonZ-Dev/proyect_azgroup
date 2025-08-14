import { TestBed } from '@angular/core/testing';

import { ItemsServiceService } from './items-service.service';

describe('ItemsServiceService', () => {
  let service: ItemsServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ItemsServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
