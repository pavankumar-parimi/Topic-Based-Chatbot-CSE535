import { Component, ElementRef, ViewChild } from '@angular/core';
import {ChatService} from './chat.service'
import { Query } from './query';
import { ChartOptions } from 'chart.js';
import { Subject } from 'rxjs';
import { IDropdownSettings, } from 'ng-multiselect-dropdown';
import { ChartConfiguration } from 'chart.js';
import {BaseChartDirective} from 'ng2-charts'


class Message {
  constructor(public author: string, public content: string) {}
}
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'chatbot';
  show:boolean = false;
  type:string = "";
  @ViewChild(BaseChartDirective) chart: BaseChartDirective

  public barChartLegend = true;
  public barChartPlugins = [];

  public barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: ['Education','Environment','HealthCare','Politics','Technology'],
    datasets: [
      { data: [0, 0, 0, 0, 0], label: 'Relevant' },
      { data: [0, 0, 0, 0, 0], label: 'Irrelevant' }
    ]
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: false,
  };


  show1:boolean = false;
  messages: Message[] = [];
  conversation = new Subject<Message[]>();
  value: string = '';
  dropdownSettings:IDropdownSettings={};
  // visulization_data = {};
  @ViewChild('chat') private myScroll: ElementRef;
  topicsList = [
    { item_id: 1, item_text: 'Politics' },
    { item_id: 2, item_text: 'Environment' },
    { item_id: 3, item_text: 'Technology' },
    { item_id: 4, item_text: 'HealthCare' },
    { item_id: 5, item_text: 'Education' }
  ];

  selectedItems = [
    { item_id: 1, item_text: 'Politics' },
    { item_id: 2, item_text: 'Environment' },
    { item_id: 3, item_text: 'Technology' },
    { item_id: 4, item_text: 'HealthCare' },
    { item_id: 5, item_text: 'Education' }
  ];

  // queries: Query[] = [];
  query:Query = {message:"",topics:[],type:""};
  visualizationData : any = {
    'Education': {
      'Relevant':0,
      'Irrelevant':0
    },
    'Environment': {
      'Relevant':0,
      'Irrelevant':0
    },
    'HealthCare': {
      'Relevant':0,
      'Irrelevant':0
    },
    'Politics': {
      'Relevant':0,
      'Irrelevant':0
    },
    'Technology': {
      'Relevant':0,
      'Irrelevant':0
    }
  };
  constructor(public chatService: ChatService){}
  ngOnInit() {
    this.dropdownSettings = {
      idField: 'item_id',
      textField: 'item_text',
    };
      this.conversation.subscribe((val) => {
      this.messages = this.messages.concat(val);
      // console.log(this.messages)  
    });
    setInterval(()=> {
      this.barChartData.datasets[0].data = [this.visualizationData.Education.Relevant,
        this.visualizationData.Environment.Relevant,
        this.visualizationData.HealthCare.Relevant,
        this.visualizationData.Politics.Relevant,
        this.visualizationData.Technology.Relevant]
      this.barChartData.datasets[1].data = [this.visualizationData.Education.Irrelevant,
        this.visualizationData.Environment.Irrelevant,
        this.visualizationData.HealthCare.Irrelevant,
        this.visualizationData.Politics.Irrelevant,
        this.visualizationData.Technology.Irrelevant]
      this.barChartData.labels = ['Education','Environment','HealthCare','Politics','Technology']
      this.chart.update()
    },1000)
  }

  openChat(value: boolean) {
    this.show = !this.show
 
    if(!value) {
      this.query.message = "Cancel";
      this.query.topics = [];
      this.query.type = "";
      this.chatService.sendCloseRequest(this.query).subscribe();
      this.messages = []
      this.visualizationData = {
        'Education': {
          'Relevant':0,
          'Irrelevant':0
        },
        'Environment': {
          'Relevant':0,
          'Irrelevant':0
        },
        'HealthCare': {
          'Relevant':0,
          'Irrelevant':0
        },
        'Politics': {
          'Relevant':0,
          'Irrelevant':0
        },
        'Technology': {
          'Relevant':0,
          'Irrelevant':0
        }
      }
    }
  }

  ngAfterViewChecked() {   
    if(this.show)     
      this.myScroll.nativeElement.scrollTop = this.myScroll.nativeElement.scrollHeight;
  } 
  sendMessage(selectedItems: any) {
    // var query = {message:"",topics:[]};
    // console.log("last : ", this.queries[this.queries.length-1]);
    var bot_response = "";
    this.query.message = this.value;
    this.query.topics = selectedItems;
    this.query.type = "";
    console.log(this.query);

    // this.queries.push(query);
    // console.log("in component : ", this.queries);
    const userMessage = new Message('user', this.value);
    this.conversation.next([userMessage]);
    this.chatService.sendUserQuery(this.query).subscribe(response => {
      bot_response = response.msg.msg;
      this.type = response.msg.type;
      console.log("typeee :", this.type)
      if(bot_response == ""){
        bot_response = "I can't understand your text. Can you please repeat"
      }
      const botMessage = new Message('bot', bot_response);
      setTimeout(()=>{
        this.conversation.next([botMessage]);
      }, 1500);
    });
    this.value = '';
  }
  openTopics() {
    this.show1 = !this.show1
  }

  isRelevant(value: boolean, selectedItems: any) {
    this.query.message = value ? "Relevant" : "Irrelevant";
    this.query.topics = selectedItems;
    this.query.type = this.type;
    console.log("relevancyyyy : ", this.query);
    this.chatService.getVisualizationData(this.query).subscribe(response => {
      console.log("visualization data : ", response);
      this.visualizationData = response.msg;
    })
  }

}
