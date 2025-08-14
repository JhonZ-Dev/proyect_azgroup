import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CotizacionesComponentComponent } from './cotizaciones-component.component';

describe('CotizacionesComponentComponent', () => {
  let component: CotizacionesComponentComponent;
  let fixture: ComponentFixture<CotizacionesComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CotizacionesComponentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CotizacionesComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
