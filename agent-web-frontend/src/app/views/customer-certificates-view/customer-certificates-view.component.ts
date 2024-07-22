import {Component} from '@angular/core';
import {Location} from "@angular/common";
import {AgentApiService} from "../../services/agent-api-service/agent-api.service";
import {ActivatedRoute, RouterLink} from "@angular/router";
import {NgbModal} from "@ng-bootstrap/ng-bootstrap";
import {ConfirmModalComponent} from "../../modals/confirm-modal/confirm-modal.component";
import {delay} from "rxjs";

@Component({
  selector: 'app-customer-certificates-view',
  standalone: true,
  imports: [
    RouterLink
  ],
  templateUrl: './customer-certificates-view.component.html',
  styleUrl: './customer-certificates-view.component.scss'
})
export class CustomerCertificatesViewComponent {
  customer!: any;
  certificates: any[] = [];
  loader = false;

  constructor(
    public location: Location,
    private apiService: AgentApiService,
    private route: ActivatedRoute,
    private modal: NgbModal
  ) {
    this.route.paramMap.subscribe(params => {
      this.loader = true;
      this.apiService.customerCertificatesViewLoad({
        customerId: params.get('customerId')
      }).pipe(
        delay(600)
      ).subscribe(response => {
        this.customer = response.customer;
        this.certificates = response.certificates;
        this.loader = false;
      });
    });
  }

  delete(index: any) {
    const modalRef = this.modal.open(ConfirmModalComponent);
    modalRef.componentInstance.title = "Brisanje sertifikata";
    modalRef.componentInstance.message = "Da li ste sigurni da želite da obrišete sertifikat?"
    modalRef.componentInstance.confirmButtonText = "Obriši";
    modalRef.componentInstance.confirmButtonClass = "btn-danger";

    modalRef.closed.subscribe(value => {
      const certificate = this.certificates[index];

      this.apiService.customerCertificatesViewDelete({
        certificateId: certificate.id
      }).subscribe(response => {
        if (response.error) {

        } else {
          this.certificates.splice(index, 1);
        }
      });
    })
  }

  download(index: number) {
    const certificate = this.certificates[index];

    this.apiService.customerCertificatesDownload({
      certificateId: certificate.id
    }).subscribe(response => {
      const contentDisposition = response.headers.get('Content-Disposition') || '';
      const matches = /filename="?([^"]+)"?/.exec(contentDisposition);
      const filename = matches && matches.length > 1 ? matches[1] : 'sertifikat.pfx';

      const a = document.createElement('a');
      const objectUrl = URL.createObjectURL(response.body!);

      a.href = objectUrl;
      a.download = filename;
      document.body.appendChild(a); // This line might be necessary for some browsers
      a.click();

      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(objectUrl);
      }, 0);
    })
  }
}
