import { NgFor } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CountcotizacionesComponent } from "../../dashboard/countcotizaciones/countcotizaciones.component";
import { CountdetalleprocesoComponent } from "../../dashboard/countdetalleproceso/countdetalleproceso.component";
interface MenuOption {
  id: number;
  name: string;
  path: string | null;
  icon: string;
  sort_order: number;
  children: MenuOption[];
}
@Component({
  selector: 'app-menu-cards',
  imports: [NgFor, CountcotizacionesComponent, CountdetalleprocesoComponent],
  templateUrl: './menu-cards.component.html',
  styleUrl: './menu-cards.component.css',
  standalone: true
})
export class MenuCardsComponent {
  menuCards: MenuOption[] = [];
  constructor(private router: Router) {}
    ngOnInit(): void {
    // Lee el storage y parsea
    const userStr = localStorage.getItem('menus');
    let menuRoot: MenuOption[] = [];

    if (userStr) {
      menuRoot = JSON.parse(userStr);
    }

    // Aplana y filtra solo los que tienen path
    this.menuCards = this.extractCards(menuRoot);
  }
  
  extractCards(menus: MenuOption[]): MenuOption[] {
    // Devuelve un array de todos los hijos que tienen path
    let cards: MenuOption[] = [];
    menus.forEach(menu => {
      if (menu.path) {
        cards.push(menu);
      }
      if (menu.children && menu.children.length > 0) {
        cards = cards.concat(this.extractCards(menu.children));
      }
    });
    return cards;
  }
  
  goTo(path: string) {
    if (path) this.router.navigate([path]);
  }

}
