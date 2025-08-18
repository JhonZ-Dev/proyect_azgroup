import { TestBed } from '@angular/core/testing';

import { CountCotizacionesService } from './count-cotizaciones.service';

describe('CountCotizacionesService', () => {
  let service: CountCotizacionesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CountCotizacionesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
