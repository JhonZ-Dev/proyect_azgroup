import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FormatService {
  private formatoSubject = new BehaviorSubject<string>(localStorage.getItem('jhon_formato') || 'antiguo');
  formato$ = this.formatoSubject.asObservable();

  get formatoSeleccionado(): string {
    return this.formatoSubject.value;
  }

  set formatoSeleccionado(val: string) {
    localStorage.setItem('jhon_formato', val);
    this.formatoSubject.next(val);
  }
}
