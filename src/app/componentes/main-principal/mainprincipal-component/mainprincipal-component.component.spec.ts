import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MainprincipalComponentComponent } from './mainprincipal-component.component';

describe('MainprincipalComponentComponent', () => {
  let component: MainprincipalComponentComponent;
  let fixture: ComponentFixture<MainprincipalComponentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MainprincipalComponentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MainprincipalComponentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
