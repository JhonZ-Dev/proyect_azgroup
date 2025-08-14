import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListarCotizacionesComponent } from './listar-cotizaciones.component';

describe('ListarCotizacionesComponent', () => {
  let component: ListarCotizacionesComponent;
  let fixture: ComponentFixture<ListarCotizacionesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListarCotizacionesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListarCotizacionesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
