import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { environment } from '../../environments/environment';
import { ApiService } from '../api.service';
import { ThemeService } from '../theme/theme.service';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
  styleUrls: ['./session.component.css']
})
export class SessionComponent implements OnInit {
  platformName;
  userName;
  biosName;
  craffName;
  releaseName;
  loader = true;
  initialData = [];
  initialSessionData = [];
  selected: any;
  showIcon = true;
  showBackgroundColor = false;
  tableColor = false;
  sharableReleaseVersionLink;
  packageColumnHeadElements = ['session_name', 'host_os', 'vnc', 'created_date', 'actions'];
  textMessage: any;
  msgHideAndShow = false;
  userid;
  errorMsg;
  successMsg;
  vnc;
  url;
  deleteBtnLoader = true;

  constructor(private route: ActivatedRoute, private api: ApiService, private themeService: ThemeService, private router: Router,
              private toastr: ToastrService) {
    const userId = this.route.snapshot.paramMap.get('userId') ? this.route.snapshot.paramMap.get('userId') : '';
    const hostOS = this.route.snapshot.paramMap.get('host') ? this.route.snapshot.paramMap.get('host') : '';
    const releaseNameFromURL = this.route.snapshot.paramMap.get('releaseName') ? this.route.snapshot.paramMap.get('releaseName') : '';
    const bios = this.route.snapshot.paramMap.get('bios') ? this.route.snapshot.paramMap.get('bios') : '';
    const craff = this.route.snapshot.paramMap.get('craff') ? this.route.snapshot.paramMap.get('craff') : '';
    this.userName = userId;
    this.biosName = bios;
    this.craffName = craff;
    this.releaseName = releaseNameFromURL;
  }

  ngOnInit(): void {
    this.url = window.location.href;
    this.showIcon = true;
    this.showBackgroundColor = false;
    this.tableColor = !this.tableColor;
    this.sharableReleaseVersionLink = window.location.href;
    const releaseNameFromURL = this.route.snapshot.paramMap.get('releaseName');
    /* Session Details */
    this.api.getUserSession()
    .subscribe(sessionData => {
    if (sessionData.body.data) {
      if (sessionData.body.status === 'ok') {
        for (const ele of sessionData.body.data) {
          if (ele[0].substr(0, ele[0].indexOf('-')) === this.userName) {
            this.initialSessionData.push(ele);
          }
        }
        this.loader = false;
        this.deleteBtnLoader = false;
        this.successMsg = 'Session successfully listed for the user';
        return this.toastr.success('' + this.successMsg, 'Success', {timeOut: 5000});
      } else {
        this.loader = false;
        this.deleteBtnLoader = false;
        this.errorMsg = sessionData.body.status;
        return this.toastr.error('' + this.errorMsg, 'Error', {timeOut: 15000});
      }
    }
    }); // hide the spinner in case of error););

    this.api.getUser().subscribe(data => {
      this.userid = data.body.userid;
      return this.userid;
    });
  }

/* To copy Text from Textbox */
public copyInputMessage(inputElement): any {
  inputElement.select();
  document.execCommand('copy');
  inputElement.setSelectionRange(0, 0);
  this.textMessageFunc('Text');
}

  /* Copy to Clipboard */
  public textMessageFunc(msgText): any {
    this.textMessage = msgText + ' Copied to Clipboard';
    this.msgHideAndShow = true;
    setTimeout(() => {
      this.textMessage = '';
      this.msgHideAndShow = false;
    }, 1000);
  }

  /* Function to delete the user session */
  public deleteUserSession(sessionName: any, sessionType: any): any {
    this.deleteBtnLoader = true;
    this.api.deleteUserSession({session_name: sessionName, session_type: sessionType })
    .subscribe(
      res => {
        if (res.body.status === 'success') {
          const status = res.status;
          this.initialSessionData.slice(0, sessionName);
          for (let i = 0; i < this.initialSessionData.length; i++) {
            if ( this.initialSessionData[i] === sessionName) {
              this.initialSessionData.splice(i, 1);
            }
          }
          window.location.reload(true);
          this.successMsg = 'Session successfully deleted for the user';
          this.deleteBtnLoader = false;
          return this.toastr.success('' + this.successMsg, 'Success', {timeOut: 5000});
        } else if (res.body.status === 'nok') {
          this.errorMsg = res.body.data;
          this.deleteBtnLoader = false;
          return this.toastr.error('' + this.errorMsg, 'Error', {timeOut: 15000});
        }
      }
  );
  }

  /* Function to assign the vnc copy link in the left pane */
  public assignVNCCopyLink(vnc: any, inputElement): string {
    this.vnc = vnc;
    this.copyInputMessage(inputElement);
    return this.vnc;
  }
}
