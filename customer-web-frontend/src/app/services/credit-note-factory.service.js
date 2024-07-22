angular
    .module('app')
    .service('creditNoteFactory', creditNoteFactory);

creditNoteFactory.$inject = [];

function creditNoteFactory() {
    service = {};
    service.PRECISION = 4;
    service.create = create;
    service.clearInvoices = clearInvoices;
    service.addReturnItem = addReturnItem;
    service.removeReturnItem = removeReturnItem;
    service.addDiscountItem = addDiscountItem;
    service.removeDiscountItem = removeDiscountItem;
    service.getPayload = getPayload;
    service.getReturnItemFromAmountWithTax = getReturnItemFromAmountWithTax;
    service.getDiscountItemFromAmountWithTax = getDiscountItemFromAmountWithTax;
    service.recalculateTotals = recalculateTotals;
    service.recalculateTaxGroupTotals = recalculateTaxGroupTotals;
    service.recalculateTaxGroupLimits = recalculateTaxGroupLimits;
    return service;

    function clearInvoices(creditNote) {
        creditNote.fakture = [];
    }

    function create() {
        let creditNote = {};
        creditNote.komitent_id = undefined;
        creditNote.valuta_id = 50

        creditNote.tax_amount = 0;
        creditNote.return_amount = 0;
        creditNote.return_amount_with_tax = 0;
        creditNote.discount_amount = 0;
        creditNote.discount_amount_with_tax = 0;
        creditNote.return_and_discount_amount = 0;
        creditNote.return_and_discount_amount_with_tax = 0;

        creditNote.tax_amount_21 = 0;
        creditNote.return_amount_21 = 0;
        creditNote.return_amount_with_tax_21 = 0;
        creditNote.discount_amount_21 = 0;
        creditNote.discount_amount_with_tax_21 = 0;
        creditNote.return_and_discount_amount_21 = 0;
        creditNote.return_and_discount_amount_with_tax_21 = 0;

        creditNote.tax_amount_7 = 0;
        creditNote.return_amount_7 = 0;
        creditNote.return_amount_with_tax_7 = 0;
        creditNote.discount_amount_7 = 0;
        creditNote.discount_amount_with_tax_7 = 0;
        creditNote.return_and_discount_amount_7 = 0;
        creditNote.return_and_discount_amount_with_tax_7 = 0;

        creditNote.tax_amount_0 = 0;
        creditNote.return_amount_0 = 0;
        creditNote.return_amount_with_tax_0 = 0;
        creditNote.discount_amount_0 = 0;
        creditNote.discount_amount_with_tax_0 = 0;
        creditNote.return_and_discount_amount_0 = 0;
        creditNote.return_and_discount_amount_with_tax_0 = 0;

        creditNote.fakture_credit_note_turnover_remaining = 0;
        creditNote.fakture_credit_note_turnover_remaining_21 = 0;
        creditNote.fakture_credit_note_turnover_remaining_7 = 0;
        creditNote.fakture_credit_note_turnover_remaining_0 = 0;
        creditNote.stavkePovrata = [];
        creditNote.stavkePopusta = [];
        creditNote.fakture = [];  // view data
        creditNote.invoice_ids = [];
        creditNote.grupe_poreza = [21, 7, 0].map(function (taxRate) {
            return {
                number_of_items: 0,
                tax_rate: taxRate,
                tax_amount: 0,
                return_amount: 0,
                return_amount_with_tax: 0,
                discount_amount: 0,
                discount_amount_with_tax: 0,
                return_and_discount_amount: 0,
                return_and_discount_amount_with_tax: 0,
                fakture_credit_note_turnover_remaining: 0,
                fakture_credit_note_turnover_used: 0
            };
        });

        creditNote.iic_refs = [];

        return creditNote;
    }

    function addReturnItem(creditNote) {
        let item = {
            tax_rate: undefined,
            tax_amount: 0,
            return_amount: 0,
            return_amount_with_tax: 0,
            discount_amount: 0,
            discount_amount_with_tax: 0,
            type: 1
        };

        creditNote.stavkePovrata.push(item);

        return item;
    }


    function removeReturnItem(creditNote, index) {
        creditNote.stavkePovrata.splice(index, 1);
    }

    function addDiscountItem(creditNote) {
        let item = {
            tax_rate: undefined,
            return_amount: 0,
            return_amount_with_tax: 0,
            discount_amount: 0,
            discount_amount_with_tax: 0,
            return_and_discount_amount: 0,
            return_and_discount_amount_with_tax: 0
        };

        creditNote.stavkePopusta.push(item);

        return item;
    }

    function removeDiscountItem(creditNote, index) {
        creditNote.stavkePopusta.splice(index, 1);
    }

    function getPayload(creditNote) {
        let payload = {};
        payload.komitent_id = creditNote.komitent_id;
        payload.valuta_id = creditNote.valuta_id;
        payload.tax_amount = creditNote.tax_amount;
        payload.return_amount = creditNote.return_amount;
        payload.return_amount_with_tax = creditNote.return_amount_with_tax;
        payload.discount_amount = creditNote.discount_amount;
        payload.discount_amount_with_tax = creditNote.discount_amount_with_tax;
        payload.return_and_discount_amount = creditNote.return_and_discount_amount;
        payload.return_and_discount_amount_with_tax = creditNote.return_and_discount_amount_with_tax;

        payload.grupe_poreza = [];
        for (let ii = 0; ii < creditNote.grupe_poreza.length; ii++) {
            let taxGroup = creditNote.grupe_poreza[ii];
            if (taxGroup.return_and_discount_amount_with_tax === 0) {
                continue;
            }

            payload.grupe_poreza.push({
                tax_rate: taxGroup.tax_rate,
                tax_amount: taxGroup.tax_amount,
                return_amount: taxGroup.return_amount,
                return_amount_with_tax: taxGroup.return_amount_with_tax,
                discount_amount: taxGroup.discount_amount,
                discount_amount_with_tax: taxGroup.discount_amount_with_tax,
                return_and_discount_amount: taxGroup.return_and_discount_amount,
                return_and_discount_amount_with_tax: taxGroup.return_and_discount_amount_with_tax
            });
        }

        payload.iic_refs = angular.copy(creditNote.iic_refs);

        payload.stavke = [];
        for (let ii = 0; ii < creditNote.stavkePovrata.length; ii++) {
            let returnItem = creditNote.stavkePovrata[ii];
            payload.stavke.push({
                type: returnItem.type,
                description: returnItem.description,
                tax_rate: returnItem.tax_rate,
                tax_amount: returnItem.tax_amount,
                return_amount: returnItem.return_amount,
                return_amount_with_tax: returnItem.return_amount_with_tax,
                discount_amount: returnItem.discount_amount,
                discount_amount_with_tax: returnItem.discount_amount_with_tax
            });
        }
        for (let ii = 0; ii < creditNote.stavkePopusta.length; ii++) {
            let discountItem = creditNote.stavkePopusta[ii];
            payload.stavke.push({
                description: discountItem.description,
                type: discountItem.type,
                tax_rate: discountItem.tax_rate,
                tax_amount: discountItem.tax_amount,
                return_amount: discountItem.return_amount,
                return_amount_with_tax: discountItem.return_amount_with_tax,
                discount_amount: discountItem.discount_amount,
                discount_amount_with_tax: discountItem.discount_amount_with_tax
            });
        }

        return payload;
    }

    function getReturnItemFromAmountWithTax(description, taxRate, amountWithTax) {
        amountWithTax = new Big(amountWithTax)
        let taxMultiplier = _getTaxMultiplier(taxRate);
        let amountWithoutTax = amountWithTax.div(taxMultiplier).round(service.PRECISION);

        return {
            description: description,
            tax_rate: taxRate,
            tax_amount: amountWithTax.minus(amountWithoutTax).toNumber(),
            discount_amount: 0,
            discount_amount_with_tax: 0,
            return_amount: amountWithoutTax.toNumber(),
            return_amount_with_tax: amountWithTax.toNumber(),
            type: 1
        };
    }

    function getDiscountItemFromAmountWithTax(description, taxRate, amountWithTax) {
        amountWithTax = new Big(amountWithTax)
        let taxMultiplier = _getTaxMultiplier(taxRate);
        let amountWithoutTax = amountWithTax.div(taxMultiplier).round(service.PRECISION)

        return {
            description: description,
            tax_rate: taxRate,
            tax_amount: amountWithTax.minus(amountWithoutTax).toNumber(),
            discount_amount: amountWithoutTax.toNumber(),
            discount_amount_with_tax: amountWithTax.toNumber(),
            return_amount: 0,
            return_amount_with_tax: 0,
            type: 2
        };
    }

    function _getTaxMultiplier(taxRate) {
        return (new Big(taxRate)).div(100).plus(1).toNumber();
    }

    function recalculateTotals(creditNote) {
        let tax_amount = new Big(0);
        let return_amount = new Big(0);
        let return_amount_with_tax = new Big(0);
        let discount_amount = new Big(0);
        let discount_amount_with_tax = new Big(0);
        let return_and_discount_amount = new Big(0);
        let return_and_discount_amount_with_tax = new Big(0);

        for (let ii = 0; ii < creditNote.stavkePovrata.length; ii++) {
            let stavka = creditNote.stavkePovrata[ii];
            tax_amount = tax_amount.plus(stavka.tax_amount);
            return_amount = return_amount.plus(stavka.return_amount);
            return_amount_with_tax = return_amount_with_tax.plus(stavka.return_amount_with_tax);
            return_and_discount_amount = return_and_discount_amount.plus(stavka.return_amount);
            return_and_discount_amount_with_tax = return_and_discount_amount_with_tax.plus(stavka.return_amount_with_tax);
        }

        for (let ii = 0; ii < creditNote.stavkePopusta.length; ii++) {
            let stavka = creditNote.stavkePopusta[ii];
            tax_amount = tax_amount.plus(stavka.tax_amount);
            discount_amount = discount_amount.plus(stavka.discount_amount);
            discount_amount_with_tax = discount_amount_with_tax.plus(stavka.discount_amount_with_tax);
            return_and_discount_amount = return_and_discount_amount.plus(stavka.discount_amount);
            return_and_discount_amount_with_tax = return_and_discount_amount_with_tax.plus(stavka.discount_amount_with_tax);
        }

        creditNote.tax_amount = tax_amount.toNumber();
        creditNote.return_amount = return_amount.toNumber();
        creditNote.return_amount_with_tax = return_amount_with_tax.toNumber();
        creditNote.discount_amount = discount_amount.toNumber();
        creditNote.discount_amount_with_tax = discount_amount_with_tax.toNumber();
        creditNote.return_and_discount_amount = return_and_discount_amount.toNumber();
        creditNote.return_and_discount_amount_with_tax = return_and_discount_amount_with_tax.toNumber();
    }

    function recalculateTaxGroupTotals(creditNote) {
        for (let ii = 0; ii < creditNote.grupe_poreza.length; ii++) {
            let taxGroup = creditNote.grupe_poreza[ii];

            taxGroup.tax_amount = new Big(0);
            taxGroup.return_amount = new Big(0);
            taxGroup.return_amount_with_tax = new Big(0);
            taxGroup.discount_amount = new Big(0);
            taxGroup.discount_amount_with_tax = new Big(0);
            taxGroup.return_and_discount_amount = new Big(0);
            taxGroup.return_and_discount_amount_with_tax = new Big(0);

            for (let ii = 0; ii < creditNote.stavkePovrata.length; ii++) {
                let stavka = creditNote.stavkePovrata[ii];

                if (taxGroup.tax_rate !== stavka.tax_rate) {
                    continue;
                }

                taxGroup.tax_amount = taxGroup.tax_amount.plus(stavka.tax_amount);
                taxGroup.return_amount = taxGroup.return_amount.plus(stavka.return_amount);
                taxGroup.return_amount_with_tax = taxGroup.return_amount_with_tax.plus(stavka.return_amount_with_tax);
                taxGroup.return_and_discount_amount = taxGroup.return_and_discount_amount.plus(stavka.return_amount);
                taxGroup.return_and_discount_amount_with_tax = taxGroup.return_and_discount_amount_with_tax.plus(stavka.return_amount_with_tax);
            }

            for (let ii = 0; ii < creditNote.stavkePopusta.length; ii++) {
                let stavka = creditNote.stavkePopusta[ii];

                if (taxGroup.tax_rate !== stavka.tax_rate) {
                    continue;
                }

                taxGroup.tax_amount = taxGroup.tax_amount.plus(stavka.tax_amount);
                taxGroup.discount_amount = taxGroup.discount_amount.plus(stavka.discount_amount);
                taxGroup.discount_amount_with_tax = taxGroup.discount_amount_with_tax.plus(stavka.discount_amount_with_tax);
                taxGroup.return_and_discount_amount = taxGroup.return_and_discount_amount.plus(stavka.discount_amount);
                taxGroup.return_and_discount_amount_with_tax = taxGroup.return_and_discount_amount_with_tax.plus(stavka.discount_amount_with_tax);
            }

            taxGroup.tax_amount = taxGroup.tax_amount.round(service.PRECISION).toNumber();
            taxGroup.return_amount = taxGroup.return_amount.round(service.PRECISION).toNumber();
            taxGroup.return_amount_with_tax = taxGroup.return_amount_with_tax.round(service.PRECISION).toNumber();
            taxGroup.discount_amount = taxGroup.discount_amount.round(service.PRECISION).toNumber();
            taxGroup.discount_amount_with_tax = taxGroup.discount_amount_with_tax.round(service.PRECISION).toNumber();
            taxGroup.return_and_discount_amount = taxGroup.return_and_discount_amount.round(service.PRECISION).toNumber();
            taxGroup.return_and_discount_amount_with_tax = taxGroup.return_and_discount_amount_with_tax.round(service.PRECISION).toNumber();

            creditNote['tax_amount_' + taxGroup.tax_rate] = taxGroup.tax_amount;
            creditNote['return_amount_' + taxGroup.tax_rate] = taxGroup.return_amount;
            creditNote['return_amount_with_tax_' + taxGroup.tax_rate] = taxGroup.return_amount_with_tax;
            creditNote['discount_amount_' + taxGroup.tax_rate] = taxGroup.discount_amount;
            creditNote['discount_amount_with_tax_' + taxGroup.tax_rate] = taxGroup.discount_amount_with_tax;
            creditNote['return_and_discount_amount_' + taxGroup.tax_rate] = taxGroup.return_and_discount_amount;
            creditNote['return_and_discount_amount_with_tax_' + taxGroup.tax_rate] = taxGroup.return_and_discount_amount_with_tax;
        }
    }

    function recalculateTaxGroupLimits(creditNote) {
        for (let ii = 0; ii < creditNote.grupe_poreza.length; ii++) {
            creditNote.grupe_poreza[ii].fakture_credit_note_turnover_remaining = new Big(0);
            creditNote.grupe_poreza[ii].fakture_credit_note_turnover_used = new Big(0);
        }

        for (let ii = 0; ii < creditNote.iic_refs.length; ii++) {
            let iicRef = creditNote.iic_refs[ii];

            let taxGroup21 = creditNote.grupe_poreza.find(function (x) { return x.tax_rate === 21; });
            let remaining_21 = (new Big(iicRef.total_21)).minus(iicRef.amount_21)
            taxGroup21.fakture_credit_note_turnover_remaining = taxGroup21.fakture_credit_note_turnover_remaining.plus(remaining_21);
            taxGroup21.fakture_credit_note_turnover_used = taxGroup21.fakture_credit_note_turnover_used.plus(iicRef.amount_21);

            let taxGroup7 = creditNote.grupe_poreza.find(function (x) { return x.tax_rate === 7; });
            let remaining_7 = (new Big(iicRef.total_7)).minus(iicRef.amount_7)
            taxGroup7.fakture_credit_note_turnover_remaining = taxGroup7.fakture_credit_note_turnover_remaining.plus(remaining_7);
            taxGroup7.fakture_credit_note_turnover_used = taxGroup7.fakture_credit_note_turnover_used.plus(iicRef.amount_7);

            let taxGroup0 = creditNote.grupe_poreza.find(function (x) { return x.tax_rate === 0; });
            let remaining_0 = (new Big(iicRef.total_0)).minus(iicRef.amount_0)
            taxGroup0.fakture_credit_note_turnover_remaining = taxGroup0.fakture_credit_note_turnover_remaining.plus(remaining_0);
            taxGroup0.fakture_credit_note_turnover_used = taxGroup0.fakture_credit_note_turnover_used.plus(iicRef.amount_0);
        }

        creditNote.fakture_credit_note_turnover_remaining = (new Big(0));
        creditNote.fakture_credit_note_turnover_used = (new Big(0));
        for (let ii = 0; ii < creditNote.grupe_poreza.length; ii++) {
            let grupa_poreza = creditNote.grupe_poreza[ii];
            grupa_poreza.fakture_credit_note_turnover_remaining = grupa_poreza.fakture_credit_note_turnover_remaining.round(service.PRECISION);
            grupa_poreza.fakture_credit_note_turnover_used = grupa_poreza.fakture_credit_note_turnover_used.round(service.PRECISION);

            creditNote.fakture_credit_note_turnover_remaining = creditNote.fakture_credit_note_turnover_remaining.plus(grupa_poreza.fakture_credit_note_turnover_remaining);
            creditNote.fakture_credit_note_turnover_used = creditNote.fakture_credit_note_turnover_used.plus(grupa_poreza.fakture_credit_note_turnover_used);

            creditNote['fakture_credit_note_turnover_remaining_' + grupa_poreza.tax_rate.toString()] = grupa_poreza.fakture_credit_note_turnover_remaining;
            creditNote['fakture_credit_note_turnover_used_' + grupa_poreza.tax_rate.toString()] = grupa_poreza.fakture_credit_note_turnover_used;

            grupa_poreza.fakture_credit_note_turnover_remaining = grupa_poreza.fakture_credit_note_turnover_remaining.toNumber()
            grupa_poreza.fakture_credit_note_turnover_used = grupa_poreza.fakture_credit_note_turnover_used.toNumber()
        }

        creditNote.fakture_credit_note_turnover_remaining = creditNote.fakture_credit_note_turnover_remaining.toNumber();
        creditNote.fakture_credit_note_turnover_used = creditNote.fakture_credit_note_turnover_used.toNumber();
    }
}
