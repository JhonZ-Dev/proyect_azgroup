import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CountcotizacionesComponent } from './countcotizaciones.component';

describe('CountcotizacionesComponent', () => {
  let component: CountcotizacionesComponent;
  let fixture: ComponentFixture<CountcotizacionesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CountcotizacionesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CountcotizacionesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
