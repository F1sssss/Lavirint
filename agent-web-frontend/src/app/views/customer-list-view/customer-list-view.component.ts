import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {debounceTime, delay, finalize, Subject, switchMap, tap} from "rxjs";
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {CompanyData} from "../../models/CompanyData";
import {
  CompanyListOnSearchInputChangeRequest,
  PagedData
} from "../../services/agent-api-service/agent-api-dto";
import {NgbModal} from "@ng-bootstrap/ng-bootstrap";
import {ConfirmModalComponent} from "../../modals/confirm-modal/confirm-modal.component";

@Component({
  selector: 'app-company-list',
  templateUrl: './customer-list-view.component.html',
  styleUrls: ['./customer-list-view.component.scss']
})
export class CustomerListViewComponent implements OnInit, AfterViewInit {
  @ViewChild("searchInput") searchInput = {} as ElementRef<HTMLInputElement>

  pagedData: PagedData<CompanyData> = {
    pageStart: 0,
    pageEnd: 0,
    pageIndex: 0,
    itemsPerPage: 10,
    pageNumber: 1,
    totalItems: 0,
    totalPages: 0,
    items: []
  };

  searchQuery: string = '';

  private searchSubject = new Subject<CompanyListOnSearchInputChangeRequest>();
  viewStatus: string = 'loading';

  constructor(
    private agentApiService: AgentApiService,
    private modal: NgbModal
  ) {

  }

  pages: Array<number> = [];
  page: number = 1;

  ngOnInit(): void {
    this.searchSubject
      .pipe(
        tap(() => {
          this.viewStatus = 'loading'
        }),
        debounceTime(1000),
        switchMap((requestData) => {
          return this.agentApiService.customerListViewLoad(requestData);
        })
      )
      .subscribe(
        (response) => {
          this.pagedData = response.pagedData;
          this.viewStatus = 'viewing';
          for (let ii = 0; ii < this.pagedData.totalItems; ii++) {
            this.pages.push(ii + 1);
          }
        }
      );

    this.searchSubject.next({
      pageNumber: 1,
      itemsPerPage: 10,
      filters: {
        query: ''
      }
    });
  }

  ngAfterViewInit() {
    setTimeout(() => {
      this.searchInput.nativeElement.focus();
    }, 0);
  }

  onSearchInputChange(): void {
    this.viewStatus = 'loading';
    this.searchSubject.next({
      pageNumber: 1,
      itemsPerPage: 10,
      filters: {
        query: this.searchQuery
      }
    });
  }

  // onPageChange(event: PageEvent) {
  //   this.viewStatus = 'loading';
  //   this.searchSubject.next({
  //     pageNumber: event.pageIndex + 1,
  //     itemsPerPage: 10,
  //     filters: {
  //       query: this.searchQuery
  //     }
  //   });
  // }

  setCompanyActiveStatus(company: CompanyData) {
    // const dialogConfig = new MatDialogConfig<ButtonsDialogData>();
    // dialogConfig.disableClose = true;
    // dialogConfig.autoFocus = true;
    //
    // dialogConfig.data = {
    //   title: 'Promjena aktivacije klijenta',
    //   description: 'Odaberite opciju u skladu željenim ishodom',
    //   buttons:
    //   [
    //     {
    //       label: 'Deaktiviraj',
    //       value: false,
    //       color: 'warn'
    //     },
    //     {
    //       label: 'Aktiviraj',
    //       value: true,
    //       color: 'primary'
    //     }
    //   ]
    // };

    // const dialogRef: MatDialogRef<ButtonsDialogComponent, any> = this.dialog.open(ButtonsDialogComponent, dialogConfig);
    // dialogRef.afterClosed().subscribe(data => {
    //   if (!data.isConfirmed) {
    //     return;
    //   }
    //
    //   this.viewStatus = 'updating';
    //   const postData = {
    //     companyId: company.id,
    //     newStatus: data.value
    //   }
    //
    //   this.agentApiService
    //     .views__company__list__update_active_status(postData)
    //     .pipe(delay(600))
    //     .pipe(
    //       finalize(() => {
    //         this.viewStatus = 'viewing';
    //       })
    //     ).subscribe(response => {
    //       company.isActive = response.newStatus;
    //   });
    // });
  }

  setCompanyTaxpayerStatus(company: CompanyData) {
    // const dialogConfig = new MatDialogConfig<ButtonsDialogData>();
    // dialogConfig.disableClose = true;
    // dialogConfig.autoFocus = true;
    //
    // dialogConfig.data = {
    //   title: 'Promjena aktivacije klijenta',
    //   description: 'Odaberite opciju u skladu željenim ishodom',
    //   buttons:
    //     [
    //       {
    //         label: 'Nije PDV',
    //         value: false,
    //         color: 'warn'
    //       },
    //       {
    //         label: 'Je PDV',
    //         value: true,
    //         color: 'primary'
    //       }
    //     ]
    // };

    // const dialogRef: MatDialogRef<ButtonsDialogComponent> = this.dialog.open(ButtonsDialogComponent, dialogConfig);
    // dialogRef.afterClosed().subscribe(data => {
    //   if (data.isConfirmed) {
    //     this.viewStatus = 'updating';
    //     this.agentApiService.views__company__list__update_taxpayer_status({
    //       companyId: company.id,
    //       newStatus: data.value
    //     }).pipe(
    //       delay(600),
    //       finalize(() => {
    //         this.viewStatus = 'viewing';
    //       })
    //     ).subscribe((response) => {
    //       company.isTaxpayer = response.newStatus;
    //     });
    //   }
    // });
  }

  toggleEnabled(item: CompanyData) {
    const modalRef = this.modal.open(ConfirmModalComponent);
    if (item.isActive) {
      modalRef.componentInstance.title = "Promjena prava pristupa";
      modalRef.componentInstance.message = "Da li ste sigurni da želite da omogućite pristup operaterima klijenta " + item.name + "?";
      modalRef.componentInstance.confirmButtonText = "Onemogući pristup";
      modalRef.componentInstance.confirmButtonClass = "btn-danger";
    } else {
      modalRef.componentInstance.title = "Promjena prava pristupa";
      modalRef.componentInstance.message = "Da li ste sigurni da želite da omogućite pristup operaterima klijenta " + item.name + "?";
      modalRef.componentInstance.confirmButtonText = "Omogući pristup";
    }

    modalRef.closed.subscribe((result: any) => {
      this.agentApiService.customerListViewUpdateActiveStatus({
        companyId: item.id,
        newStatus: !item.isActive
      }).pipe(
        delay(600),
        finalize(() => {
          this.viewStatus = 'viewing';
        })
      ).subscribe((response) => {
        item.isActive = response.newStatus;
      });
    });
  }

  toggleVatStatus(item: CompanyData) {
    const modalRef = this.modal.open(ConfirmModalComponent);
    if (item.isTaxpayer) {
      modalRef.componentInstance.title = "Promjena poreskog statusa";
      modalRef.componentInstance.message = "Da li ste sigurni da želite da uključite status poreskog obveznika za klijenta " + item.name + "?";
      modalRef.componentInstance.confirmButtonText = "Isključi status poreskog obveznika";
    } else {
      modalRef.componentInstance.title = "Promjena poreskog statusa";
      modalRef.componentInstance.message = "Da li ste sigurni da želite da uključite status poreskog obveznika za klijenta " + item.name + "?";
      modalRef.componentInstance.confirmButtonText = "Uključi status poreskog obveznika";
    }

    modalRef.closed.subscribe((result: any) => {
      this.agentApiService.customerListViewUpdateTaxpayerStatus({
        companyId: item.id,
        newStatus: !item.isTaxpayer
      }).pipe(
        delay(600),
        finalize(() => {
          this.viewStatus = 'viewing';
        })
      ).subscribe((response) => {
        item.isTaxpayer = response.newStatus;
      });
    });
  }

  prevPage() {
    this.viewStatus = 'loading';
    this.searchSubject.next({
      pageNumber: this.pagedData.pageNumber - 1,
      itemsPerPage: 10,
      filters: {
        query: this.searchQuery
      }
    });
  }

  nextPage() {
    this.viewStatus = 'loading';
    this.searchSubject.next({
      pageNumber: this.pagedData.pageNumber + 1,
      itemsPerPage: 10,
      filters: {
        query: this.searchQuery
      }
    });
  }
}
