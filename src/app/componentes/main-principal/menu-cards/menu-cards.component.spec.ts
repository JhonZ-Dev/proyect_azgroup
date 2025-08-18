import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MenuCardsComponent } from './menu-cards.component';

describe('MenuCardsComponent', () => {
  let component: MenuCardsComponent;
  let fixture: ComponentFixture<MenuCardsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MenuCardsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MenuCardsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
