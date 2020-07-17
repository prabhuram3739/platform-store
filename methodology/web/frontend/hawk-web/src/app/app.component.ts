import { Component, OnInit, Input } from '@angular/core';
import { ThemeService } from './theme/theme.service';
import { Router } from '@angular/router';
import { transition, trigger, query, style, animate, group, animateChild } from '@angular/animations';
import { HttpClient } from '@angular/common/http';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  animations: [
    trigger('myAnimation', [
      transition('* => *', [
        query(
          ':enter',
          [style({ opacity: 0 })],
          { optional: true }
        ),
        query(
          ':leave',
           [style({ opacity: 1 }), animate('0.3s', style({ opacity: 0 }))],
          { optional: true }
        ),
        query(
          ':enter',
          [style({ opacity: 0 }), animate('0.3s', style({ opacity: 1 }))],
          { optional: true }
        )
      ])
    ])
  ] // register the animations
})
export class AppComponent implements OnInit {
  title = 'hawk-web';
  addLightColor = false;
  messages = this.http.get<any []>('http://localhost:3000');
  userid;

  constructor(private themeService: ThemeService, private http: HttpClient, private api: ApiService) {
  }

  ngOnInit(): void {
    const active = this.themeService.getActiveTheme();
    this.api.getUser().subscribe(data => {
      this.userid = data.body.userid;
      return this.userid;
    });
  }

  toggle() {
    const active = this.themeService.getActiveTheme() ;
    if (active.name === 'light') {
      this.themeService.setTheme('dark');
      this.addLightColor = true;
    } else {
      this.themeService.setTheme('light');
      this.addLightColor = false;
    }
  }
}
