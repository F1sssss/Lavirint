angular
    .module('app')
    .controller('CreditNoteCreateController', CreditNoteCreateController);

CreditNoteCreateController.$inject = [
    '$rootScope', '$q', '$state', '$uibModal', 'api', 'viewData', 'fisModal', 'fisGui', 'stampac', 'creditNoteFactory',
    'fisCustomerApi'
];

function CreditNoteCreateController(
    $rootScope, $q, $state, $uibModal, api, viewData, fisModal, fisGui, stampac, creditNoteFactory,
    fisCustomerApi
) {
    let ctrl = this;

    ctrl.invoiceSelectMode = false;
    ctrl.isLoadingInvoices = false;
    ctrl.stranica = null;
    ctrl.buyer = undefined;
    ctrl.creditNote = creditNoteFactory.create();
    ctrl.iic_ref = {
        iic: '',
        issue_datetime: '',
        amount_21: 0,
        amount_7: 0,
        amount_0: 0,
        amount_exempt: 0
    };

    ctrl.onBuyerTypeaheadSelect = onBuyerTypeaheadSelect;
    ctrl.removeBuyer = removeBuyer;
    ctrl.showBuyerUpdateModal = showBuyerUpdateModal;
    ctrl.onInvoicePageChange = onInvoicePageChange;
    ctrl.onSubmitButton = onSubmitButton;
    ctrl.findRemaningTurnover = findRemaningTurnover;
    ctrl.showReturnItemModal = showReturnItemModal;
    ctrl.showDiscountItemModal = showDiscountItemModal;
    ctrl.onInvoiceSelect = onInvoiceSelect;
    ctrl.addExternalInvoices = addExternalInvoices;

    ctrl.poreskeStope = angular.copy(viewData.poreske_stope);

    function onBuyerTypeaheadSelect($model) {
        ctrl.creditNote = creditNoteFactory.create();
        ctrl.buyer = $model;
        ctrl.creditNote.komitent_id = $model.id;

        ctrl.filters = {
            ordinal_id: undefined,
            broj_stavki_po_stranici: 10,
            broj_stranice: 1,
            total_price_gte: undefined,
            total_price_lte: undefined,
            fiscalization_date_gte: undefined,
            fiscalization_date_lte: undefined,
            payment_type_id: undefined,
            client_id: [$model.id],
            not_payment_type_id: [6],
            invoice_type_ids: [1]
        }

        ctrl.isLoadingInvoices = true;

            return fisCustomerApi.views__credit_note_create__on_buyer_typeahead_select(ctrl.filters).then(function(data) {
            ctrl.isLoadingInvoices = false;
            ctrl.stranica = data.stranica;
        });
    }

    function removeBuyer() {
        ctrl.buyer = undefined;
        ctrl.creditNote = creditNoteFactory.create();
    }

    function showBuyerUpdateModal() {
        fisModal.buyerUpdateModal(ctrl.buyer.id).then(function(result) {
            if (result.isConfirmed) {
                ctrl.creditNote.komitent = ctrl.komitent;
                ctrl.creditNote.komitent_id = ctrl.komitent.id;
            }
        });
    }

    function onInvoicePageChange() {
        ctrl.isLoadingInvoices = true;
        return fisCustomerApi.views__credit_note_create__on_invoice_page_change(ctrl.filters).then(function(data) {
            ctrl.stranica = data.stranica;
            ctrl.isLoadingInvoices = false;
        });
    }

    function validateTurnover() {
        return;
        ctrl.mainForm.$setValidity('turnover', true);
        ctrl.mainForm.$setValidity('noInvoices', true);

        if (ctrl.creditNote.fakture_credit_note_turnover_remaining === 0) {
            ctrl.mainForm.$setValidity('noInvoices', false);
            ctrl.mainForm.$setValidity('turnover', false);
            return;
        }

        if (ctrl.creditNote.return_amount_with_tax > 0 &&
            ctrl.creditNote.fakture_credit_note_turnover_remaining < ctrl.creditNote.return_amount_with_tax) {
            ctrl.mainForm.$setValidity('notEnoughTurnover', false);
            ctrl.mainForm.$setValidity('turnover', false);
        } else {
            ctrl.mainForm.$setValidity('notEnoughTurnover', true);
        }

        if (ctrl.creditNote.return_and_discount_amount_with_tax_21 > 0 &&
            ctrl.creditNote.fakture_credit_note_turnover_remaining_21 < ctrl.creditNote.return_and_discount_amount_with_tax_21) {
            ctrl.mainForm.$setValidity('notEnoughTurnover21', false);
            ctrl.mainForm.$setValidity('turnover', false);
        } else {
            ctrl.mainForm.$setValidity('notEnoughTurnover21', true);
        }

        if (ctrl.creditNote.return_and_discount_amount_with_tax_7 > 0 &&
            ctrl.creditNote.fakture_credit_note_turnover_remaining_7 < ctrl.creditNote.return_and_discount_amount_with_tax_7) {
            ctrl.mainForm.$setValidity('notEnoughTurnover7', false);
            ctrl.mainForm.$setValidity('turnover', false);
        } else {
            ctrl.mainForm.$setValidity('notEnoughTurnover7', true);
        }

        if (ctrl.creditNote.return_and_discount_amount_with_tax_0 > 0 &&
            ctrl.creditNote.fakture_credit_note_turnover_remaining_0 < ctrl.creditNote.return_and_discount_amount_with_tax_0) {
            ctrl.mainForm.$setValidity('notEnoughTurnover0', false);
            ctrl.mainForm.$setValidity('turnover', false);
        } else {
            ctrl.mainForm.$setValidity('notEnoughTurnover0', true);
        }
    }

    function validateItems() {
        if (ctrl.creditNote.return_and_discount_amount === 0) {
            ctrl.mainForm.$setValidity('noReturnAndDiscount', false);
        } else {
            ctrl.mainForm.$setValidity('noReturnAndDiscount', true);
        }
    }

    function onSubmitButton() {
        ctrl.mainForm.$setSubmitted();
        if (ctrl.creditNote.iic_refs.length === 0) {
            ctrl.mainForm.$setValidity('noInvoices', false);
        } else {
            ctrl.mainForm.$setValidity('noInvoices', true);
        }
        validateTurnover();
        validateItems();
        if (ctrl.mainForm.$invalid) {
            return;
        }

        fisGui.wrapInLoader(function () {
            let payload = creditNoteFactory.getPayload(ctrl.creditNote);

            return fisCustomerApi.views__credit_note_create__on_fiscalize(payload).then(function(data) {
                return data;
            });
        }).then(function(data) {
            if (data.is_success) {
                return stampac.stampajKnjiznoOdobrenje(data.credit_note.id).then(function() {
                    return $state.transitionTo($state.current, {}, {
                        reload: true, inherit: false
                    });
                });
            } else {
                return fisModal.confirm({
                    headerText: 'Greška',
                    headerIcon: 'fa fa-exclamation-triangle text-danger',
                    bodyText: 'Knjižno odobrenje nije fiskalizovano. '
                });
            }
        })
    }

    function findRemaningTurnover(taxRate, invoice) {
        for (let ii = 0; ii < invoice.grupe_poreza.length; ii++) {
            let grupaPoreza = invoice.grupe_poreza[ii];
            if (grupaPoreza.porez_procenat === taxRate) {
                return grupaPoreza.credit_note_turnover_remaining;
            }
        }
    }

    function showReturnItemModal(item, $index) {
        let payload = {};
        payload.item = null;
        payload.options = {};
        payload.options.type = 'return';

        if (item) {
            payload.item = {};
            payload.item.description =  item.description;
            payload.item.taxRate =  item.tax_rate;
            payload.item.amount =  item.return_amount_with_tax;
        }

        fisModal.creditNoteItemModal(payload).result.then(function(data) {
            if (data.action === 'cancel') {
                return;
            }

            if (data.action === 'delete') {
                creditNoteFactory.removeReturnItem(ctrl.creditNote, $index);
            }

            if (data.action === 'save') {
                if (!item) {
                    item = creditNoteFactory.addReturnItem(ctrl.creditNote);
                }
                let newItem = creditNoteFactory.getReturnItemFromAmountWithTax(data.item.description, data.item.taxRate, data.item.amount);
                angular.extend(item, newItem)
                creditNoteFactory.recalculateTaxGroupTotals(ctrl.creditNote);
                creditNoteFactory.recalculateTotals(ctrl.creditNote);
                validateItems();
            }
        });
    }

    function showDiscountItemModal(item, $index) {
        let payload = {};
        payload.item = null;
        payload.options = {};
        payload.options.type = 'discount';

        if (item) {
            payload.item = {};
            payload.item.description = item.description;
            payload.item.taxRate = item.tax_rate;
            payload.item.amount = item.discount_amount_with_tax;
        }

        fisModal.creditNoteItemModal(payload).result.then(function(data) {
            if (data.action === 'cancel') {
                return;
            }

            if (data.action === 'delete') {
                creditNoteFactory.removeDiscountItem(ctrl.creditNote, $index);
            }

            if (data.action === 'save') {
                if (!item) {
                    item = creditNoteFactory.addDiscountItem(ctrl.creditNote);
                }
                let newItem = creditNoteFactory.getDiscountItemFromAmountWithTax(data.item.description, data.item.taxRate, data.item.amount);
                angular.extend(item, newItem);
                creditNoteFactory.recalculateTaxGroupTotals(ctrl.creditNote);
                creditNoteFactory.recalculateTotals(ctrl.creditNote);
                validateItems();
            }
        });
    }

    function onInvoiceSelect(action, invoice, event) {
        if (action === 'add') {
            return fisModal.creditNoteTurnoverUsedModal({ invoice: invoice }).then(function(result) {
                if (result.action === 'cancel') {
                    event.shouldSelect = false;
                }

                if (result.action === 'confirmed') {
                    ctrl.creditNote.iic_refs.push({
                        iic: invoice.iic,
                        invoice_id: invoice.id,
                        verification_url: invoice.efi_verify_url,
                        issue_datetime: invoice.datumfakture,
                        amount_21: result.data.amount_21,
                        amount_7: result.data.amount_7,
                        amount_0: result.data.amount_0,
                        amount_exempt: result.data.amount_exempt,
                        total_21: result.data.total_21,
                        total_7: result.data.total_7,
                        total_0: result.data.total_0,
                        total_exempt: result.data.total_exempt
                    });

                    creditNoteFactory.recalculateTaxGroupLimits(ctrl.creditNote);
                    validateTurnover();
                    ctrl.invoiceSelectMode = false;
                }
            });
        } else {
            let defer = $q.defer();
            defer.promise.then(function() {
                let index = ctrl.creditNote.iic_refs.indexOf(x => {
                    if (x.id === invoice.id) {
                        return x;
                    }
                });
                ctrl.creditNote.iic_refs.splice(index, 1);
            })
            defer.resolve();
            return defer.promise;
        }
    }

    function addExternalInvoices() {
        return fisModal.creditNoteExternalInvoice().then(function(result) {
            ctrl.creditNote.iic_refs.push({
                iic: result.data.iic,
                invoice_id: null,
                verification_url: result.data.verification_url,
                issue_datetime: result.data.issue_datetime,
                amount_21: result.data.amount_21,
                amount_7: result.data.amount_7,
                amount_0: result.data.amount_0,
                amount_exempt: result.data.amount_exempt,
                total_21: result.data.total_21,
                total_7: result.data.total_7,
                total_0: result.data.total_0,
                total_exempt: result.data.total_exempt
            });

            creditNoteFactory.recalculateTaxGroupLimits(ctrl.creditNote);
        });
    }
}
