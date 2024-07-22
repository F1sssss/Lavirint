export enum INVOICE_TYPES {
  REGULAR = 1,
  CANCELLATION = 2,
  SUMMARY = 3,
  PERIODICAL = 4,
  ADVANCE = 5,
  CREDIT_NOTE = 6,
  CORRECTIVE = 7,
  ERROR_CORRECTIVE = 8,
  REGULAR_TEMPLATE = 9
}

export const INVOICE_TYPES_CONCRETE = [
  {id: 1, description: 'Redovni račun'},
  {id: 2, description: 'Storno račun'},
  {id: 3, description: 'Zbirni račun'},
  {id: 4, description: 'Periodični račun'},
  {id: 5, description: 'Avansni račun'},
  {id: 6, description: 'Knjižno odobrenje'},
  {id: 7, description: 'Korektivni račun'},
  {id: 8, description: 'Korekcija računa sa greškom'},
  {id: 9, description: 'Predračun'}
]
