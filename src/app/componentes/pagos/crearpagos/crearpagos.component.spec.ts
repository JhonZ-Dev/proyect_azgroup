import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CrearpagosComponent } from './crearpagos.component';

describe('CrearpagosComponent', () => {
  let component: CrearpagosComponent;
  let fixture: ComponentFixture<CrearpagosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CrearpagosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CrearpagosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
