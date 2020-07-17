import { Directive, OnInit, OnDestroy, ElementRef } from '@angular/core';
import { ThemeService } from './theme.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Theme } from './symbols';

@Directive({
  selector: '[appTheme]'
})
export class ThemeDirective implements OnInit {

  private unsubscribe = new Subject();
  constructor(
    private elementRef: ElementRef,
    private themeService: ThemeService
  ) {}

  ngOnInit() {
    const active = this.themeService.getActiveTheme();
    if (active) {
      this.updateTheme(active);
    }
    this.themeService.themeChange.pipe(takeUntil(this.unsubscribe))
      .subscribe((theme: Theme) => this.updateTheme(theme));
  }

  updateTheme(theme: Theme) {
    for (const key in theme.properties) {
      this.elementRef.nativeElement.style.setProperty(key, theme.properties[key]);
    }
  }

}
