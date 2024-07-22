import {FormControl, ValidationErrors} from "@angular/forms";

export class FisValidators {

  static regex = /^\d*$/

  static companyIdentificationNumber(control: FormControl): ValidationErrors | null {
    const value = control.value;

    if (!value) {
      return null;
    }

    if (typeof value === 'string' && !FisValidators.regex.test(value)) {
      return {
        pattern: true
      }
    }

    if (value.length !== 8 && value.length !== 13) {
      return {
        length: true
      }
    }

    return null;
  }
}
