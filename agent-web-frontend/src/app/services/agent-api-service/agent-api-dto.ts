import {CountryData} from "../../models/CompanyData";

export interface AuthLoginRequest {
  username: string;
  password: string;
}

export interface AuthLoginResponse {
  errorMessage: string | null;
}

export interface CompanyListOnSearchInputChangeRequest {
  pageNumber: number;
  itemsPerPage: number;
  filters: {
    query: string
  }
}

export interface PagedData<T> {
  pageIndex: number;
  pageNumber: number;
  itemsPerPage: number;
  totalItems: number;
  totalPages: number;
  pageStart: number;
  pageEnd: number;
  items: Array<T>;
}

export interface CompanyParamIdGeneralInfoOnLoadResponse {
  company: {
    id: number;
    name: string;
    isActive: boolean;
    identificationNumber: string;
    taxNumber: string;
    isTaxpayer: boolean;
    adress: string;
    city: string;
    bankAccount: string;
    phoneNumber: string;
    emailAddress: string;
    countryId: number;
    country: CountryData;
  }
}
