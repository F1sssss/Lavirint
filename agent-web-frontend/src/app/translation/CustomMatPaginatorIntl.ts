import {Injectable, OnDestroy} from '@angular/core';
import {Subject} from "rxjs";
import {MatPaginatorIntl} from "@angular/material/paginator";

@Injectable()
export class CustomMatPaginatorIntl extends MatPaginatorIntl implements OnDestroy {
  unsubscribe: Subject<void> = new Subject<void>();

  override itemsPerPageLabel: string = 'Stavki po stranici:';
  override nextPageLabel: string = 'Sledeća';
  override previousPageLabel: string = 'Prethodna';
  override firstPageLabel: string = 'Prva';
  override lastPageLabel: string = 'Poslednja';
  OF_LABEL = 'od';

  constructor() {
    super();
  }

  ngOnDestroy() {
    this.unsubscribe.next();
    this.unsubscribe.complete();
  }

  override getRangeLabel = (page: number, pageSize: number, length: number) => {
    if (length === 0) {
      return `0 ${this.OF_LABEL} 0`;
    }

    const sIndex = page * pageSize;
    const eIndex = (sIndex < length)
      ? Math.min(sIndex + pageSize, length)
      : sIndex + pageSize;

    return `${sIndex + 1} - ${eIndex} ${this.OF_LABEL} ${length}`;
  }
}
