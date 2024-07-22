export enum TAX_RATES {
  TAX_27 = 1,
  TAX_7 = 2,
  TAX_0 = 3,
  TAX_EXEMPT = 4
}

export const TAX_RATE_CONCRETE = [
  {
    id: 1,
    percentage: 21.000000,
    description: '21%'
  },
  {
    id: 2,
    percentage: 7.000000,
    description: '7%'
  },
  {
    id: 3,
    percentage: 0.000000,
    description: '0%'
  },
  {
    id: 4,
    percentage: null,
    description: 'Oslobođeno poreza'
  }
]
