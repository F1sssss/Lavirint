import {Component, Input, OnInit} from '@angular/core';
import {NgbTooltip} from "@ng-bootstrap/ng-bootstrap";
import * as console from "console";

@Component({
  selector: 'customer-certificate-expiration-badge',
  standalone: true,
  imports: [
    NgbTooltip
  ],
  templateUrl: './customer-certificate-expiration-badge.component.html',
  styleUrl: './customer-certificate-expiration-badge.component.scss'
})
export class CustomerCertificateExpirationBadgeComponent implements OnInit{
  @Input() dateString!: string | Date;
  date!: Date;
  classValue: string = '';
  tooltip!: string;

  constructor(
  ) {

  }

  private recalculate() {
    if (this.dateString === null) {
      this.classValue = 'bg-danger-subtle';
      this.tooltip = 'Nema sertifkata';
      return;
    }

    const diff = this.date.getTime() - new Date().getTime();
    if (diff <= 0) {
      this.classValue = 'bg-danger-subtle';
      this.tooltip = 'Istekao prije ' + this.format(diff);
    } else if (diff < 604800000) {
      this.classValue = 'bg-danger-subtle';
      this.tooltip = 'Ističe za ' + this.format(diff);
    } else if (diff < 2592000000) {
      this.classValue = 'bg-warning-subtle';
      this.tooltip = 'Ističe za ' + this.format(diff);
    } else {
      this.classValue = 'bg-success-subtle';
      this.tooltip = 'Ističe za ' + this.format(diff);
    }
  }

  format(milliseconds: number) {
    // Convert milliseconds to total seconds
    const totalSeconds = Math.abs(Math.floor(milliseconds / 1000));

    // Calculate days, hours, and minutes directly from total seconds
    const days = Math.floor(totalSeconds / (60 * 60 * 24));
    const hours = Math.floor((totalSeconds % (60 * 60 * 24)) / (60 * 60));
    const minutes = Math.floor((totalSeconds % (60 * 60)) / 60);
    const seconds = totalSeconds % 60; // Remaining seconds

    // Format the output
    if (days > 0) {
      if (days === 1 || (days >= 21 && days % 10 === 1)) {
        return days + ' dan';
      } else {
        return days + ' dana';
      }
    } else {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
  }

  ngOnInit(): void {
    this.date = new Date(this.dateString);
    this.recalculate();
    setInterval(() => {
      this.recalculate();
    }, 1000)
  }
}
