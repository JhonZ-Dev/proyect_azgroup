import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { DrawerModule } from 'primeng/drawer';
import { ButtonModule } from 'primeng/button';
import { Ripple } from 'primeng/ripple';
import { AvatarModule } from 'primeng/avatar';
import { StyleClass } from 'primeng/styleclass';
import { Drawer } from 'primeng/drawer';
import { SidebarServiceService } from '../../servicios/sidebar/sidebar-service.service';
import { CommonModule } from '@angular/common';
import { MenuItem, MenuserviceService } from '../../servicios/menu-service/menuservice.service';
import { Observable } from 'rxjs';
import { RouterLink } from '@angular/router';
@Component({
  selector: 'app-sidebar-component',
  imports: [DrawerModule, ButtonModule, Ripple, AvatarModule, CommonModule, RouterLink],
  templateUrl: './sidebar-component.component.html',
  styleUrl: './sidebar-component.component.css',
  standalone: true
})
export class SidebarComponentComponent {
  visible$: any;
  menus$!: Observable<MenuItem[]>;
  constructor(public sidebarService: SidebarServiceService, private menuService: MenuserviceService) {
    this.visible$ = this.sidebarService.visible$;
  }

  @ViewChild('drawerRef') drawerRef!: Drawer;
  @Output() visibleChange = new EventEmitter<boolean>();
  visible = false;
  ngOnInit() {
    this.menus$ = this.menuService.menus$;
  }

  toggle() {
    this.visible = !this.visible;
    this.visibleChange.emit(this.visible);
  }
  // closeCallback(e: Event): void {
  //   this.drawerRef.close(e);
  // }
   closeCallback(event: any) {
    this.sidebarService.setVisible(false);
  }
  // Manejador para el two-way binding
  onVisibleChange(v: boolean) {
    this.sidebarService.setVisible(v);
  }


}
