export interface CountryData {
  id: number;
  nameMontenegrin: string;
  nameEnglish: string;
}

export interface CompanyData {
  certificateExpirationDate: string;
  id: number;
  name: string;
  isActive: boolean;
  isTaxpayer: boolean;
  identificationNumber: string;
}
