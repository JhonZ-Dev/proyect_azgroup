// src/app/shared/directives/uppercase.directive.ts
import { Directive, ElementRef, HostListener } from '@angular/core';
import { NgControl } from '@angular/forms';

@Directive({
  selector: '[appUppercase]',
  standalone: true,
})
export class UppercaseDirective {
  constructor(private ngControl: NgControl, private el: ElementRef<HTMLInputElement>) {}

  @HostListener('input')
  onInput() {
    const value = (this.el.nativeElement.value ?? '').toUpperCase();
    // actualiza valor del control SIN disparar loops
    this.ngControl.control?.setValue(value, { emitEvent: false });
    // refleja en el input
    this.el.nativeElement.value = value;
  }
}
