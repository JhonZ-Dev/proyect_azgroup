import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { api_items } from '../../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class ItemsServiceService {

  private urlItems: string = api_items.apiUrl;
  constructor(private http: HttpClient) { }

  //crear items
  // public createitems(payloadItems: any[]){
  //   this.http.post<any>(this.urlItems+"crear-item",payloadItems);
  // }
  private httpOptions() {
  const token = localStorage.getItem('access_token');   // o donde lo guardes
  return {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    }),
    withCredentials: false  // si no usas cookies
  };
}
   public createItem(payload: any) {
    const headers = new HttpHeaders({
      'Content-Type':  'application/json',
      Authorization:   `Bearer ${localStorage.getItem('access_token')}`
    });
    return this.http.post<any>(
      `${this.urlItems}crear-item`,
      payload,
      { headers }
    );
  }
}
