import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';



export interface MenuItem {
  id: number;
  name: string;
  path?: string;
  icon?: string;
  sort_order: number;
  children: MenuItem[];
}
@Injectable({
  providedIn: 'root'
})

export class MenuserviceService {
private _menus = new BehaviorSubject<MenuItem[]>([]);
  readonly menus$ = this._menus.asObservable();

  constructor() { this.loadFromStorage();}

  loadFromStorage() {
    const raw = localStorage.getItem('menus');
    const data: MenuItem[] = raw ? JSON.parse(raw) : [];
    this._menus.next(data);
  }
}
