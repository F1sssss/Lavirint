import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {environment} from "../../../environments/environment";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class AgentApiService {
  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient
  ) {

  }

  dataServiceLoad(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/data-service/load`,
      data,
      { withCredentials: true }
    );
  }

  loginViewSubmit(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/login-view/submit`,
      data,
      { withCredentials: true }
    );
  }

  customerInsertViewSubmit(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-insert-view/submit`,
      data,
      { withCredentials: true }
    );
  }

  customerUpdateViewLoad(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-update-view/load`,
      data,
      { withCredentials: true }
    );
  }

  customerUpdateViewSubmit(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-update-view/submit`,
      data,
      { withCredentials: true }
    );
  }

  customerListViewLoad(
    data: any
  ): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-list-view/load`,
      data,
      { withCredentials: true }
    );
  }

  customerListViewUpdateActiveStatus(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-list-view/update_active_status`,
      data,
      { withCredentials: true }
    );
  }

  customerListViewUpdateTaxpayerStatus(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-list-view/update_taxpayer_status`,
      data,
      { withCredentials: true }
    );
  }

  customerCertificatesViewLoad(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-certificates-view/load`,
      data,
      { withCredentials: true }
    );
  }

  customerCertificatesViewDelete(data: any): Observable<any> {
    return this.http.post<any>(
      `${this.apiUrl}/customer-certificates-view/delete`,
      data,
      { withCredentials: true }
    );
  }

  customerCertificateUploadViewLoad(data: any) {
    return this.http.post<any>(
      `${this.apiUrl}/customer-certificate-upload-view/load`,
      data,
      { withCredentials: true }
    );
  }

  customerCertificateUploadViewSubmit(data: any) {
    return this.http.post<any>(
      `${this.apiUrl}/customer-certificate-upload-view/submit`,
      data,
      { withCredentials: true }
    );
  }

  customerCertificatesDownload(data: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/customer-certificates-view/download`,
      data,
      { responseType: 'blob', observe: 'response' }
    );
  }

  customerBusinessUnitsListViewLoad(data: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/customer-business-units-view/load`,
      data,
      { withCredentials: true }
    );
  }
}
