import { Component } from '@angular/core';
import {NgbActiveModal} from "@ng-bootstrap/ng-bootstrap";

@Component({
  selector: 'app-confirm-modal',
  templateUrl: './confirm-modal.component.html',
  styleUrls: ['./confirm-modal.component.scss']
})
export class ConfirmModalComponent {
  cancelButtonText = "Odustani";
  confirmButtonText = "Potvrdi";
  confirmButtonClass = "btn-primary";
  title!: string;
  message!: string;

  constructor(
    protected activeModal: NgbActiveModal
  ) {
  }
}
