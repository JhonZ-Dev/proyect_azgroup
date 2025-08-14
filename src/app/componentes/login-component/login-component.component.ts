import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Login } from '../modelos/login/login';
import { LoginServiceService } from '../servicios/login/login-service.service';
import { Router } from '@angular/router';
import { AuthService } from '../servicios/auth/auth.service';

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

// iniciarSesion(){
//   this._loginService.login(this.username, this.password).subscribe({
//     next:(res)=>{console.log("Inicio sesion exitoso",res)
//         // Guarda el token
//       localStorage.setItem('access_token', res.access_token);
//       localStorage.setItem('menus',JSON.stringify(res.menus))
//       this.redirectToInicioSesion();
//     },
//     error:()=>{console.log("Error iniciado sesion")}
//   })
// }
iniciarSesion(){
  this._loginService.login(this.username, this.password).subscribe({
    next: (res) => {
      console.log("Inicio sesion exitoso", res);
      this.auth.setToken(res.access_token); // <— usa el servicio
      localStorage.setItem('menus', JSON.stringify(res.menus));
      this.redirectToInicioSesion();
    },
    error: () => { console.log("Error iniciado sesion") }
  })
}

redirectToInicioSesion(){
  this.router.navigate(['/menu-principal']);
}

}
