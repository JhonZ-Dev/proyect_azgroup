import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SidebarServiceService {

  constructor() { }
  private _visible = new BehaviorSubject(false);
  readonly visible$ = this._visible.asObservable();

  toggle() {
    this._visible.next(!this._visible.value);
  }

  setVisible(v: boolean) {
    this._visible.next(v);
  }
}
