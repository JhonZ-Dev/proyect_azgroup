import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListProcesosComponent } from './list-procesos.component';

describe('ListProcesosComponent', () => {
  let component: ListProcesosComponent;
  let fixture: ComponentFixture<ListProcesosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ListProcesosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListProcesosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
