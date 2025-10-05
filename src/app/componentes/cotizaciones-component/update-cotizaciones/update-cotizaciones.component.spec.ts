import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateCotizacionesComponent } from './update-cotizaciones.component';

describe('UpdateCotizacionesComponent', () => {
  let component: UpdateCotizacionesComponent;
  let fixture: ComponentFixture<UpdateCotizacionesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdateCotizacionesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateCotizacionesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
