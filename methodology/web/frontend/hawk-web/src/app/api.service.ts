import { Injectable, EventEmitter } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient, HttpResponse, HttpHeaders } from '@angular/common/http';
import { Package } from './package';
import { Observable } from 'rxjs';

const API_URL = environment.apiUrl;
// const localAPIURL = environment.localApiUrl;

@Injectable()
export class ApiService {
  private options = { headers: new HttpHeaders().set('Set-Cookie', 'HttpOnly; Secure;SameSite=Strict') };
  constructor(private http: HttpClient) {
  }

  public getUser(): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/userdata', { observe: 'response' });
  }

  // API: GET /data
  public getAllData(): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/listplatforms', { observe: 'response' });
  }

  // API: GET /platform with the version
  public getPlatformsFromVersion(version: any): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/listplatforms', { params: {
      simics_version: version.simics_version,
    }, observe: 'response' });
  }

  // API: GET /hostos
  public getHostOS(): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/hostos', { observe: 'response' });
  }

  // API: GET /logout
  public logOut(): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/logout', { observe: 'response' });
  }

  // API: POST /session
  public createSessionDetails(res: any): Observable<any> {
    return this.http.get<Package[]>(API_URL + '/createsession/', { params: {
      session_type: res.session_type,
      simics_version: res.simics_version,
      platform: res.platform,
      // tslint:disable-next-line:object-literal-shorthand
      version: res.version,
      host: res.host
    }, observe: 'response' });
  }

  // To get the user session details
  public getUserSession(): Observable<HttpResponse<any>> {
    return this.http.get<any>(API_URL + '/listsessions', { observe: 'response' });
  }

  // To delete the user session details
  public deleteUserSession(res): Observable<HttpResponse<any>> {
    return this.http.delete<any>(API_URL + '/deletesession', { params: {
      session_name: res.session_name,
      session_type: res.session_type
    }, observe: 'response' });
  }

  // To format the workweek in the JSON to the date format to sort
  public formatDate(date: any, dateFormat: any): any {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) {
      month = '0' + month;
    }
    if (day.length < 2) {
      day = '0' + day;
    }
    if (dateFormat === 'yyyy/mm/dd') {
      return [year, month, day].join('-');
    } else if (dateFormat === 'dd/mm/yyyy') {
      return [day, month, year].join('-');
    } else if (dateFormat === 'mm/dd/yyyy') {
      return [month, day, year].join('-');
    }
}
}
