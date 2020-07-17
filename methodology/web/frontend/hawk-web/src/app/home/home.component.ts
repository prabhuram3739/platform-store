import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, OnDestroy, ChangeDetectorRef, } from '@angular/core';
import { environment } from '../../environments/environment';
import { ApiService } from '../api.service';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { HighchartsService } from '../highcharts.service';
import * as Highcharts from 'highcharts';
import { ToastrService } from 'ngx-toastr';

// we can now access environment.apiUrl
const API_URL = environment.apiUrl;

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  @ViewChild('charts') public chartEl: ElementRef;
  filterText;
  filteredData = [];
  loader = true;
  launchBtnLoader = true;
  releasesDetails = [];
  releaseNames = [];
  releaseDetail = [];
  releaseNamesUnfiltered = [];
  allReleases = [];
  platformName;
  countOfReleses;
  latestRelease;
  latestBuildTime;
  navbarOpen = false;
  isChecked;
  isCheckedName;
  showDetails = false;
  selectedCount = 0;
  chartData = [];
  chartDataContents = [];
  platformCount = 0;
  platformArray = [];
  type;
  isDisabled = true;
  selectedIndex;
  selectedVersionIndex;
  modelDescShort;
  selected: any;
  showBackgroundColor = false;
  clickedPlatformName;
  clickedReleaseName;
  clickedHost;
  selectedBios;
  selectedCraff;
  backgroundColor;
  userId = '';
  tempArray = [];
  errorMsg;
  successMsg;
  sessionName;
  vnc;

simicsVersions: any[] = [
  { name: 'simics-5', value: '5', total: 0, selected: false },
  { name: 'simics-6', value: '6', total: 0, selected: false }
];
hostOS: any[] = [];
biosValues: any[] = [
  { name: 'bios1', value: 'bios1' },
  { name: 'bios2', value: 'bios2' },
  { name: 'bios3', value: 'bios3' },
  { name: 'bios4', value: 'bios4' }
];
craffValues: any[] = [
  { name: 'craff1', value: 'craff1' },
  { name: 'craff2', value: 'craff2' },
  { name: 'craff3', value: 'craff3' },
  { name: 'craff4', value: 'craff4' }
];
selectedVersion: string[] = [];
sharableReleaseVersionLink;
selectedRelease: string[] = [];
selectedHost: string[] = [];
userid;

  constructor(private api: ApiService, private router: Router, private hcs: HighchartsService, private http: HttpClient,
              private toastr: ToastrService) { }

  ngOnInit(): void {
    this.platformName = '';
    this.countOfReleses = '';
    this.latestRelease = '';
    this.latestBuildTime = '';
    this.selectedIndex = '';
    this.selectedVersionIndex = '';
    this.modelDescShort = '';
    this.showBackgroundColor = false;
    this.clickedPlatformName = '';
    this.clickedReleaseName = '';
    this.clickedHost = '';
    this.selectedBios = '';
    this.selectedCraff = '';
    this.vnc = '';

    this.api.getAllData()
      .subscribe(data => {
        for (const platformName of Object.keys(data.body.data)) {
          const obj = {platform: platformName, releases: [{releaseName: data.body.data[platformName]}] };
          this.platformArray.push(obj);
      }
        const platform = 'platform';
        /*  Platform Array Manipulation */
        // tslint:disable-next-line:prefer-for-of
        for (let i = 0; i < this.platformArray.length; i++) {
          // tslint:disable-next-line:prefer-for-of
          for (let j = 0; j < this.platformArray[i].releases.length; j++) {
            this.platformArray[i].releases[j][platform] = this.platformArray[i].platform.toLowerCase();
            this.releaseNames.push(this.platformArray[i].releases[j]);
          }
        }
        this.releasesDetails = this.releaseNames;
        this.releaseNamesUnfiltered.length = 0;
        this.allReleases.length = 0;
        this.filteredData = this.platformArray;
        this.loader = false;
        this.launchBtnLoader = false;

        /* Simics Version Chart */
        this.simicsVersions[0].total = this.platformArray.filter((a) => {
          return a.sim_version === 'simics-5';
        }).length;
        this.simicsVersions[1].total = this.platformArray.filter((a) => {
          return a.sim_version === 'simics-6';
        }).length;
        for (let i = 0; i < this.simicsVersions.length; i++) {
          this.chartData[i] = [this.simicsVersions[i].name, this.simicsVersions[i].total];
        }
      }); // hide the spinner in case of error);
    this.api.getUser().subscribe(data => {
      this.userid = data.body.userid;
      return this.userid;
    });

        // Get the Host OS
    this.api.getHostOS().subscribe(data => {
     if (data.body.status === 'ok') {
        this.hostOS = data.body.data;
     } else if (data.body.status === 'nok') {
        this.errorMsg = data.body.data;
        return this.toastr.error('' + this.errorMsg, 'Error', {timeOut: 15000});
      }
    });
  }

   // Get the Release Detail based on the release name
   public getPlatformDetail(platformName: any, releaseName: any): any {
    // Call the API to read the data from the JSON and filter the results based on the search text
    this.api.getAllData()
    .subscribe(data => {
      this.releaseNamesUnfiltered = this.releaseNames.filter(
        (releases) => (releases.platform.includes(platformName))
      );

      this.selected = releaseName;
      this.showBackgroundColor = !this.showBackgroundColor;
      this.onReleaseChange(platformName, releaseName);
      this.loader = false;
    });
    return this.releaseNamesUnfiltered;
}

// On release change, get the sharable release version url
public onReleaseChange(platformName: string, releaseName: string): any {
  const index = this.selectedRelease.indexOf(releaseName);
  this.clickedPlatformName = platformName;
  this.clickedReleaseName = releaseName;
  this.sharableReleaseVersionLink = '';
  if (index === -1) {
    this.selectedRelease.length = 0;
    this.selectedRelease.push(releaseName);
  } else {
    this.selectedRelease.splice(index, 1);
  }
  this.sharableReleaseVersionLink = window.location.protocol + '//' + window.location.host
  + '/platform/' + platformName + '/' + releaseName;
  return this.sharableReleaseVersionLink;
}

  /* Change the version and the model */
  public onVersionChange(version: string): any {
    const index = this.selectedVersion.indexOf(version);
    this.selectedIndex = '';
    this.showDetails = false;
    this.allReleases.length = 0;
    this.releaseNamesUnfiltered.length = 0;
    if (index === -1) {
      this.selectedVersion.push(version);
      this.selectedCount = this.selectedVersion.length;
      /* Call appropriate function based on the checkbox value */
      if (this.selectedVersion.includes(version)) {
        if (this.selectedVersion.length !== 0) {
          this.api.getPlatformsFromVersion({ simics_version: version })
          .subscribe(
            data => {
              this.platformArray.length = 0;
              for (const platformName of Object.keys(data.body.data)) {
                const obj = { platform: platformName, releases: [{releaseName: data.body.data[platformName]}] };
                this.platformArray.push(obj);
            }
            }
        );
        }
        this.loader = false;
        return this.platformArray;
      }
     } else {
      this.selectedCount--;
      this.selectedVersion.splice(index, 1);
      if (this.selectedVersion.length !== 0) {
        this.api.getPlatformsFromVersion({ simics_version: version })
        .subscribe(
          data => {
            this.platformArray.length = 0;
            for (const platformName of Object.keys(data.body.data)) {
              const obj = { platform: platformName, releases: [{releaseName: data.body.data[platformName]}] };
              this.platformArray.push(obj);
          }
          }
      );
      } else {
        this.platformArray = this.filteredData;
      }
      if (this.selectedVersion.length === 0) {
        this.platformArray = this.filteredData;
      }
      return this.platformArray;
    }
  }

  /* Clear all the seclection in the Model Types */
  public clearSelection(): any {
    this.simicsVersions = this.simicsVersions.filter(h => {
      h.selected = false;
      return true;
    });
    this.selectedVersion.length = 0;
    this.platformArray = this.filteredData;
    this.allReleases.length = 0;
    this.clickedPlatformName = '';
    this.clickedReleaseName = '';
    this.clickedHost = '';
    this.selectedBios = '';
    this.selectedCraff = '';
    this.selectedCount = 0;
  }

  public isSelectedRelease(releaseName: string): any {
    return this.selectedRelease.indexOf(releaseName) >= 0;
  }

  public isSelectedHost(host: string): any {
    return this.selectedHost.indexOf(host) >= 0;
  }

  public isActive(item): any {
    return this.selected === item;
  }

  public isActiveHost(item): any {
    return this.selectedHost === item;
  }

  public isSelectedVersion(version): any {
    return this.selectedVersion.indexOf(version) >= 0;
  }

  // Get all the platform details
  public getAllPlatforms(filterText): any {
    if (filterText === '') {
      this.releaseNames = this.releasesDetails;
      this.platformArray.length = 0;
      this.api.getAllData()
      .subscribe(data => {
        for (const platformName of Object.keys(data.body.data)) {
          const obj = {platform: platformName, releases: [{releaseName: data.body.data[platformName]}] };
          this.platformArray.push(obj);
      }
        this.releaseNames = this.platformArray.filter(o =>
          // tslint:disable-next-line:max-line-length
          Object.keys(o).some(k => typeof o[k] === 'string' ? o[k].toLowerCase().includes(filterText.toLowerCase()) : '')
        );
        this.loader = false;
      });
      return this.releaseNames;
    } else {
      // Call the API to read the data from the JSON and filter the results based on the search text
      this.api.getAllData()
      .subscribe(data => {
        this.releaseNames = this.releasesDetails.filter(
          (platforms) => (platforms.platform.toLowerCase().includes(filterText.toLowerCase()))
        );
        this.platformArray = this.platformArray.filter(o =>
          // tslint:disable-next-line:max-line-length
          Object.keys(o).some(k => typeof o[k] === 'string' ? o[k].toLowerCase().includes(filterText.toLowerCase()) : '')
        );
        this.releaseNamesUnfiltered = this.releaseNames;
        this.loader = false;
      });
      return this.releaseNames;
    }
  }

  // Pass the platform name to the overview panel
  public passName($event: any, type: any, i: number, id, versionContainerID): any {
    this.type = type;
    this.selectedIndex = i;
    const el = document.getElementById(id);
    el.scrollIntoView({behavior: 'smooth'});
    window.scrollTo(0, 0);

    const e2 = document.getElementById(versionContainerID);
    e2.scrollIntoView({behavior: 'smooth'});
    window.scrollTo(0, 0);
    this.clickedPlatformName = $event.platform;
    this.releaseNamesUnfiltered.length = 0;
    // Call the API to read the data from the JSON and filter the results based on the search text
    this.api.getAllData()
    .subscribe(data => {
      if (type === 'platform') {
        this.allReleases = this.platformArray.filter(
          (releases) => (releases.platform.includes($event.platform))
        );
        this.platformName = this.allReleases[0].platform;
        this.countOfReleses = this.allReleases[0].releases[0].releaseName.length;
        this.latestRelease = this.allReleases[0].releases[0].releaseName[0];
      }
      this.showDetails = true;
      this.loader = false;
    });
    return this.allReleases;
  }

// Platform Details on click on each platform
public getDetail($event: any, i: number, id): any {
    const platformName = $event.platform;
    const releaseName = $event.releases[0].releaseName;
    const el = document.getElementById(id);
    el.scrollIntoView({behavior: 'smooth'});
    window.scrollTo(0, 0);
    this.selectedIndex = i;
    this.releaseNames = this.releasesDetails;
  }

/* Pass the host change */
public onHostChange(host: any): any {
  this.backgroundColor = true;
  const index = this.selectedHost.indexOf(host);
  this.clickedHost = host;
  this.isDisabled = false;
  if (index === -1) {
    this.selectedHost = host;
  } else {
    this.selectedHost.splice(index, 1);
  }
}

/* Pass the host change */
public onBiosChange(bios: any): any {
  this.clickedHost = bios;
}

/* Pass the host change */
public onCraffChange(craff: any): any {
  this.clickedHost = craff;
}

/* Pass the BIOS change */
public biosChange(bios: any): any {
  return this.selectedBios = bios;
}

/* Pass the Craff change */
// tslint:disable-next-line:typedef
public craffChange(craff: any): any {
  return this.selectedCraff = craff;
}

/* Bios Text Box Change */
public onBiosTxtBoxChangeEvent(txtValue: any): void {
  this.selectedBios = txtValue;
}

/* Craff Text Box Change */
public onCraffTxtBoxChangeEvent(txtValue: any): void {
  this.selectedCraff = txtValue;
}

  /* function to post the data to the sessions page */
  public createSession(): any {
  const vncTarget = 'http://127.0.0.1:8887/vncviewer.exe';
  const sessionType = 'simulation';
  const simicsVersion = '6.0';
  this.launchBtnLoader = true;
  this.vnc = '';
  // tslint:disable-next-line:max-line-length
  this.api.createSessionDetails({session_type: sessionType, simics_version: simicsVersion, platform: this.clickedPlatformName, version: this.clickedReleaseName, host: this.clickedHost
  })
  .subscribe(
    res => {
      if (res.body.status === 'ok') {
        this.sessionName = res.body.data[0];
        this.vnc = res.body.data[1];
        this.successMsg = 'Session successfully created for ' + this.userid;
        this.launchBtnLoader = false;
        this.isDisabled = true;
        return this.toastr.success('' + this.successMsg, 'Success', {timeOut: 5000});
      } else if (res.body.status === 'nok') {
        this.errorMsg = '' + res.body.data;
        this.launchBtnLoader = false;
        return this.toastr.error('' + this.errorMsg, 'Error', {timeOut: 15000});
      }
    }
);
}

/* Router navigate to sessions page */
  public sessionsPage(param1: any): any {
    this.router.navigate(['/sessions', param1]);
  }
}
