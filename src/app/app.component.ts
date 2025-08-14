import { ChangeDetectorRef, Component, ElementRef, Inject, inject, OnDestroy, OnInit, PLATFORM_ID, ViewChild } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { PrimeNG } from 'primeng/config';
import { PRIMENG_ES } from './i18n/primeng-es';
import { CommonModule, NgClass, NgIf } from '@angular/common';
import { Editor } from 'primeng/editor';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent{
  @ViewChild('fileInput') fileInput!: ElementRef<HTMLInputElement>;

  

  public constructor() { }

  title = 'Proyecto';

  /**CAMBIAR A ESPAÑOL */
  private primeconfig = inject(PrimeNG)


}




