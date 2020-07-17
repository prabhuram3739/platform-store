import { Component, OnInit, Input } from '@angular/core';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit {
myimage1 = 'assets/images/model-search-white-transparent-64.png';
loginUrl;
userid;
  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.api.getUser().subscribe(data => {
      this.userid = data.body.userid;
      return this.userid;
    });
  }

  /* Function to log out */
  public logOut(): any {
    this.api.logOut().subscribe(data => {
      this.loginUrl = data.url;
      console.log(this.loginUrl);
      return this.loginUrl;
    });
  }

}
