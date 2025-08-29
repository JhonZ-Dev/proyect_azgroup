import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CountdetalleprocesoComponent } from './countdetalleproceso.component';

describe('CountdetalleprocesoComponent', () => {
  let component: CountdetalleprocesoComponent;
  let fixture: ComponentFixture<CountdetalleprocesoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CountdetalleprocesoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CountdetalleprocesoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
