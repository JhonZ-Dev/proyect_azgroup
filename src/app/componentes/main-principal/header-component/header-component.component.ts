import { Component, ViewChild } from '@angular/core';
import { SidebarServiceService } from '../../servicios/sidebar/sidebar-service.service';
import { ButtonModule } from 'primeng/button';
import { Popover } from 'primeng/popover';
import { PopoverModule } from 'primeng/popover';
import { AvatarModule } from 'primeng/avatar';
import { OverlayBadgeModule } from 'primeng/overlaybadge';
import { LoginServiceService } from '../../servicios/login/login-service.service';
import { AuthService } from '../../servicios/auth/auth.service';
@Component({
  selector: 'app-header-component',
  imports: [ButtonModule, Popover, PopoverModule, AvatarModule, OverlayBadgeModule],
  templateUrl: './header-component.component.html',
  styleUrl: './header-component.component.css',
  standalone: true
})
export class HeaderComponentComponent {
  constructor(public sidebarService: SidebarServiceService, private _loginService: LoginServiceService,
    private auth: AuthService
  ) { }
  @ViewChild('op') op!: Popover;
 userInitial: string = '';
  ngOnInit() {
    const username = this._loginService.getUsername();
    if (username) {
      this.userInitial = username.charAt(0).toUpperCase();
    }
  }
  toggleSidebar() {
    this.sidebarService.toggle();
  }
  toggle(event: any) {
    this.op.toggle(event);
  }
  logout() { this.auth.logout(); }
}
