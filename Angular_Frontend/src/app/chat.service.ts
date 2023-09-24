import { EventEmitter, Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Query } from './query';

const httpOptions = {
  headers: new HttpHeaders({ 'Content-Type': 'application/json' })
};

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  list1Event: EventEmitter<any> = new EventEmitter();
  private userUrl = 'http://127.0.0.1:5000'; 
  constructor(private http: HttpClient) {}
 

  sendUserQuery(query: Query) : Observable<any> {
    console.log("in service : ", query);
    return this.http.post(this.userUrl+'/query', query, httpOptions);
  }

  getVisualizationData(query: Query) : Observable<any> {
    console.log("in service : ", query);
    return this.http.post(this.userUrl+'/visualize', query, httpOptions)
  }

  sendCloseRequest(query: Query) : Observable<any> {
    console.log("in service : ", query);
    return this.http.post(this.userUrl+'/close', query, httpOptions);
  }
}
