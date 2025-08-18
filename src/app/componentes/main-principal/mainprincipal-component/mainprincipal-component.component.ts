import { Component } from '@angular/core';
import { HeaderComponentComponent } from "../header-component/header-component.component";
import { SidebarComponentComponent } from "../sidebar-component/sidebar-component.component";
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { SidebarServiceService } from '../../servicios/sidebar/sidebar-service.service';
import { MenuCardsComponent } from "../menu-cards/menu-cards.component";

@Component({
  selector: 'app-mainprincipal-component',
  imports: [SidebarComponentComponent, CommonModule, RouterOutlet, HeaderComponentComponent],
  templateUrl: './mainprincipal-component.component.html',
  styleUrl: './mainprincipal-component.component.css',
  standalone:true
})
export class MainprincipalComponentComponent {
  constructor(public sidebarService:SidebarServiceService){}
 sidebarOpen = false;

  onSidebarToggle(open: boolean) {
    this.sidebarOpen = open;
  }
}
