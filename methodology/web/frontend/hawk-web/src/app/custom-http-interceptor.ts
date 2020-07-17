import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable()
export class CustomHttpInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    const hardCodedToken = '1d38d128-0671-4121-8084-f6332a992a40';
    req = req.clone ({
      setHeaders: {
        Authorization: `Bearer ${hardCodedToken}`
      }
    });
    return next.handle(req)
    .pipe(
      catchError((error: HttpErrorResponse) => {
        return throwError(error);
      }));
  }
}
