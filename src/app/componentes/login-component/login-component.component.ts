import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Login } from '../modelos/login/login';
import { LoginServiceService } from '../servicios/login/login-service.service';
import { Router } from '@angular/router';
import { AuthService } from '../servicios/auth/auth.service';
import { finalize } from 'rxjs';

@Component({
  selector: 'app-login-component',
  imports: [FormsModule, CommonModule],
  templateUrl: './login-component.component.html',
  styleUrl: './login-component.component.css',
  standalone:true
})
export class LoginComponentComponent {
  constructor(private _loginService:LoginServiceService, private router:Router, private auth: AuthService ){}
login:Login
username:'';
password:'';
loading = false;



// iniciarSesion(){
//   this._loginService.login(this.username, this.password).subscribe({
//     next: (res) => {
//       console.log("Inicio sesion exitoso", res);
//       this.auth.setToken(res.access_token); // <— usa el servicio
//       localStorage.setItem('menus', JSON.stringify(res.menus));
//       this.redirectToInicioSesion();
//     },
//     error: () => { console.log("Error iniciado sesion") }
//   })
// }
iniciarSesion() {
    if (!this.username || !this.password) return;

    this.loading = true;
    this._loginService.login(this.username, this.password)
      .pipe(finalize(() => this.loading = false))
      .subscribe({
        next: (res) => {
          this.auth.setToken(res.access_token);
          localStorage.setItem('menus', JSON.stringify(res.menus));
          this.router.navigate(['/menu-principal']);
        },
        error: (err) => {
          // El interceptor ya mostró un mensaje global,
          // pero aquí puedes afinar comportamiento local:
          if (err?.status === 401) {
            // ejemplo: destacar campos / limpiar password
            this.password = '';
          }
          // Si quisieras mostrar TU propio mensaje, puedes leer:
          // const msg = err?.error?.detail || err?.statusText || 'Error';
          // y mostrarlo con tu propio Toast local.
        }
      });
  }

redirectToInicioSesion(){
  this.router.navigate(['/menu-principal']);
}

}
