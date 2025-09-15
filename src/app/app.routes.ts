import { Routes } from '@angular/router';
import { LoginComponentComponent } from './componentes/login-component/login-component.component';
import { MainprincipalComponentComponent } from './componentes/main-principal/mainprincipal-component/mainprincipal-component.component';
import { CotizacionesComponentComponent } from './componentes/cotizaciones-component/cotizaciones-component.component';
import { ListarCotizacionesComponent } from './componentes/cotizaciones-component/listar-cotizaciones/listar-cotizaciones.component';
import { PagosComponent } from './componentes/pagos/pagos/pagos.component';
import { CrearpagosComponent } from './componentes/pagos/crearpagos/crearpagos.component';
import { loggedInGuard } from './guards/logged-in.guard';
import { authChildGuard, authGuard } from './guards/auth.guard';
import { MenuCardsComponent } from './componentes/main-principal/menu-cards/menu-cards.component';
import { CountcotizacionesComponent } from './componentes/dashboard/countcotizaciones/countcotizaciones.component';
import { ListProcesos } from './componentes/modelos/procesos/procesos';
import { ListProcesosComponent } from './componentes/procesos/list-procesos/list-procesos.component';



export const routes: Routes = [
    { path: '', redirectTo: '/login', pathMatch: 'full' },
    {path:'login', component:LoginComponentComponent, canActivate: [loggedInGuard]},
    {path:'menu-principal', component:MainprincipalComponentComponent,
      canActivate: [authGuard],
      canActivateChild: [authChildGuard],
      children:[
        {path: '', component: MenuCardsComponent },
        {path:'cotizaciones', component:CotizacionesComponentComponent},
        {path:'listar-cotizaciones', component:ListarCotizacionesComponent},
        {path:'listar-pagos', component:PagosComponent},
        {path:'listar-pagos-cot', component:CrearpagosComponent},
        {path:'count', component:CountcotizacionesComponent},
        {path:'list-procesos', component:ListProcesosComponent},


      ]
    },
     // 404 opcional
  { path: '**', redirectTo: '/login' }
  
    
];
