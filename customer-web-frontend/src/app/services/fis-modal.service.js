angular
    .module('app')
    .service('fisModal', fisModal);

fisModal.$inject = ['$q', '$uibModal', 'fisConfig', 'api', 'invoiceFactory'];

function fisModal($q, $uibModal, fisConfig, api, invoiceFactory) {
    let service = {};
    service.confirm = confirm;
    service.confirmOrCancel = confirmOrCancel;
    service.creditNoteExternalInvoice = creditNoteExternalInvoice;
    service.creditNoteItemModal = creditNoteItemModal;
    service.creditNoteTurnoverUsedModal = creditNoteTurnoverUsedModal;
    service.duePaymentNotificationModal = duePaymentNotificationModal;
    service.invoiceBuyerSelectModal = invoiceBuyerSelectModal;
    service.invoiceItemEdit = invoiceItemEdit;
    service.invoiceItemTemplatePicker = invoiceItemTemplatePicker;
    service.invoicePriceStructure = invoicePriceStructure;
    service.invoiceScheduleModal = invoiceScheduleModal;
    service.numericInput = numericInput;
    service.buyerUpdateModal = buyerUpdateModal;
    service.buyerCreateModal = buyerCreateModal;
    service.addPaymentMethods = addPaymentMethods;
    service.deletePaymentMethod = deletePaymentMethod;
    service.distributeDifferenceEvenly = distributeDifferenceEvenly;
    service.distributeTotalEvenly = distributeTotalEvenly;
    service.depositNeededModal = depositNeededModal;
    service.invalidForm = invalidForm;
    service.certificateUpload = certificateUpload;

    return service;

    //------------------------------------------------------------------------------------------------------------------

    function confirm(data) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/confirm-modal/confirm-modal.template.html',
            controller: 'ConfirmModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {data: data}
        });

        return modalInstance.result;
    }

    function confirmOrCancel(data) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/confirm-or-cancel-modal/confirm-or-cancel-modal.template.html',
            controller: 'ConfirmOrCancelModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {data: data}
        });

        return modalInstance.result;
    }

    function creditNoteExternalInvoice() {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/credit-note-external-invoice-modal/credit-note-external-invoice-modal.template.html',
            controller: 'CreditNoteExternalInvoiceModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {  }
        });

        return modalInstance.result;
    }

    function creditNoteItemModal(modalData) {
        return $uibModal.open({
            templateUrl: 'app/modals/credit-note-item-modal/credit-note-item-modal.template.html',
            controller: 'CreditNoteItemModal',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                modalData: modalData
            }
        });
    }

    function creditNoteTurnoverUsedModal(modalData) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/credit-note-turnover-used-modal/credit-note-turnover-used-modal.template.html',
            controller: 'CreditNoteTurnoverUsedModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: { modalData: modalData }
        });

        return modalInstance.result;
    }

    function duePaymentNotificationModal(data) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/due-payment-notification-modal/due-payment-notification-modal.template.html',
            controller: 'DuePaymentNotificationModal',
            controllerAs: 'ctrl',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                initialData: data
            }
        });

        return modalInstance.result;
    }

    function invoiceBuyerSelectModal(invoice) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/invoice-buyer-select-modal/invoice-buyer-select-modal.template.html',
            controller: 'InvoiceBuyerSelectModal',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                initialData: {
                    invoice: invoice
                }
            }
        });

        return modalInstance.result;
    }

    function invoiceItemEdit(invoice, itemIndex) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/invoice-item-edit-modal/invoice-item-edit-modal.template.html',
            controller: 'InvoiceItemEditModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                initialData: {
                    invoice: invoice,
                    itemIndex: itemIndex
                }
            }
        });

        return modalInstance.result;
    }

    function invoiceItemTemplatePicker() {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/invoice-item-template-picker-modal/invoice-item-template-picker-modal.template.html',
            controller: 'InvoiceItemTemplatePickerModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fullscreen.template.html'
        });

        return modalInstance.result;
    }

    function invoicePriceStructure(invoice) {
        return $uibModal.open({
            templateUrl: 'app/modals/invoice-price-structure-modal/invoice-price-structure-modal.template.html',
            controller: 'InvoicePriceStructureModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                initialData: {
                    invoice: invoice
                }
            }
        });
    }

    function invoiceScheduleModal(invoice) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/invoice-schedule-modal/invoice-schedule-modal.template.html',
            controller: 'InvoiceScheduleModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                initialData: {
                    invoiceId: invoice.id,
                    invoiceSchedule: invoice.active_invoice_schedule
                }
            }
        });

        return modalInstance.result;
    }

    function numericInput(initialData) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/numeric-input-modal/numeric-input-modal.template.html',
            controller: 'NumericInputModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: { initialData: initialData }
        });

        return modalInstance.result;
    }

    function buyerCreateModal() {
        return $uibModal.open({
            templateUrl: 'app/modals/komitent-unos-modal/komitent-unos-modal.template.html',
            controller: 'KomitentUnosModalController',
            controllerAs: 'ctrl',
            size: 'lg',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html'
        });
    }

    function buyerUpdateModal(buyerId) {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/komitent-izmjena-modal/komitent-izmjena-modal.template.html',
            controller: 'KomitentIzmjenaModalController',
            controllerAs: 'ctrl',
            size: 'lg',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html',
            resolve: {
                komitent: api.komitent.poId.listaj(buyerId)
            }
        });

        return modalInstance.result;
    }

    // -----------------------------------------------------------------------------------------------------------------
    // Derived modals
    // -----------------------------------------------------------------------------------------------------------------

    function addPaymentMethods(invoice, updated_invoice, advance_invoice, corrective_for_advance_invoice) {
        let settings = {};
        settings.isMultiselect = true;

        if (advance_invoice) {
            settings.isCash = invoice.is_cash;
            settings.showCashTab = false;
            settings.showNonCashTab = true;
        } else if (updated_invoice !== undefined && updated_invoice !== null) {
            settings.isCash = updated_invoice.is_cash;
            settings.showCashTab = updated_invoice.is_cash;
            settings.showNonCashTab = !updated_invoice.is_cash;
        } else {
            settings.isCash = invoice.is_cash;
        }

        paymentMethodPicker(settings).then(function(result) {
            if (!result.isConfirmed) {
                return;
            }

            invoiceFactory.sortPaymentMethodTypes(result.items);

            let modal_payment_methods = [];
            if (advance_invoice) {
                let advance_payment_method = invoiceFactory.createPaymentMethod(7);
                advance_payment_method.amount = (new Big(corrective_for_advance_invoice.ukupna_cijena_prodajna))
                    .times(-1)
                    .toNumber();
                advance_payment_method.advance_invoice = advance_invoice;
                advance_payment_method.advance_invoice_id = advance_invoice.id;
                modal_payment_methods.push(advance_payment_method);
            }

            for (let ii = 0; ii < result.items.length; ii++) {
                modal_payment_methods.push(invoiceFactory.createPaymentMethod(result.items[ii].id));
                invoiceFactory.addPaymentMethodByTypeId(invoice, result.items[ii].id);
            }

            invoice.payment_methods = modal_payment_methods;
            invoice.is_cash = modal_payment_methods[0].payment_method_type.is_cash;
            invoiceFactory.recalculatePaymentMethodTotals(invoice);
        });
    }

    function deletePaymentMethod(invoice, index) {
        invoice.payment_methods.splice(index, 1);
        invoiceFactory.recalculatePaymentMethodTotals(invoice, false);
    }

    function distributeDifferenceEvenly(invoice, updated_invoice, advance_invoice) {
        let settings = {};
        settings.isMultiselect = true;

        if (advance_invoice) {
            settings.isCash = invoice.is_cash;
            settings.showCashTab = false;
            settings.showNonCashTab = true;
        } else if (updated_invoice !== undefined && updated_invoice !== null) {
            settings.isCash = updated_invoice.is_cash;
            settings.showCashTab = updated_invoice.is_cash;
            settings.showNonCashTab = !updated_invoice.is_cash;
        } else {
            settings.isCash = invoice.is_cash;
        }

        paymentMethodPicker(settings).then(function(result) {
            if (!result.isConfirmed) {
                return;
            }

            invoiceFactory.sortPaymentMethodTypes(result.items);

            let modal_payment_methods = [];
            let parts = invoiceFactory.splitAmount(invoice.payment_methods_total_difference, result.items.length);
            for (let ii = 0; ii < result.items.length; ii++) {
                let payment_method = invoiceFactory.createPaymentMethod(result.items[ii].id);
                payment_method.amount = parts[ii];
                modal_payment_methods.push(payment_method);
            }

            modal_payment_methods = invoiceFactory.mergePaymentMethods(invoice.payment_methods, modal_payment_methods);

            let bodyText = '<div class="mb-3">Načini plaćanja će biti izmijenjeni na sledeći način:</div>';
            for (let ii = 0; ii < modal_payment_methods.length; ii++) {
                let label = modal_payment_methods[ii].payment_method_type.description;
                let value = modal_payment_methods[ii].amount;

                bodyText += "<div class=\"dash-info bg-white\">\n" +
                    "            <div class=\"dash-info-start\"><span>" + label + "</span></div>\n" +
                    "            <div class=\"dash-info-spacing\"></div>\n" +
                    "            <div class=\"dash-info-end\"><span>" + value + "</span></div>\n" +
                    "        </div>";
            }

            service.confirmOrCancel({
                headerText: 'Raspoređivanje',
                bodyText: bodyText,
                confirmButtonText: 'Da, rasporedi',
                cancelButtonText: 'Odustani'
            }).then(function(result) {
                if (result.isConfirmed) {
                    invoice.payment_methods = modal_payment_methods;
                    invoice.is_cash = modal_payment_methods[0].payment_method_type.is_cash;
                    invoiceFactory.recalculatePaymentMethodTotals(invoice);
                }
            });
        });
    }

    function distributeTotalEvenly(invoice, updated_invoice, advance_invoice, corrective_for_advance_invoice) {
        if (invoice.ukupna_cijena_prodajna === 0) {
            service.confirm({
                headerText: 'Raspoređivanje',
                bodyText: 'Račun je prazan.'
            });
            return;
        }

        let settings = {};
        settings.isMultiselect = true;

        if (advance_invoice) {
            settings.isCash = invoice.is_cash;
            settings.showCashTab = false;
            settings.showNonCashTab = true;
        } else if (updated_invoice !== undefined && updated_invoice !== null) {
            settings.isCash = updated_invoice.is_cash;
            settings.showCashTab = updated_invoice.is_cash;
            settings.showNonCashTab = !updated_invoice.is_cash;
        } else {
            settings.isCash = invoice.is_cash;
        }

        paymentMethodPicker(settings).then(function(result) {
            if (!result.isConfirmed) {
                return;
            }

            invoiceFactory.sortPaymentMethodTypes(result.items);

            let modal_payment_methods = [];
            if (advance_invoice) {
                let advance_payment_method = invoiceFactory.createPaymentMethod(7);
                advance_payment_method.amount = (new Big(corrective_for_advance_invoice.ukupna_cijena_prodajna))
                    .times(-1)
                    .toNumber();
                advance_payment_method.advance_invoice = advance_invoice;
                advance_payment_method.advance_invoice_id = advance_invoice.id;
                modal_payment_methods.push(advance_payment_method);
            }

            let amount = (new Big(invoice.ukupna_cijena_prodajna));
            for (let ii = 0; ii < modal_payment_methods.length; ii++) {
                amount = amount.minus(modal_payment_methods[ii].amount);
            }
            amount = amount.toNumber();


            let parts = invoiceFactory.splitAmount(amount, result.items.length);
            for (let ii = 0; ii < result.items.length; ii++) {
                let payment_method = invoiceFactory.createPaymentMethod(result.items[ii].id);
                payment_method.amount = parts[ii];
                modal_payment_methods.push(payment_method);
            }

            let bodyText = '<div class="mb-3">Načini plaćanja će biti izmijenjeni na sledeći način:</div>';
            for (let ii = 0; ii < modal_payment_methods.length; ii++) {
                let label = modal_payment_methods[ii].payment_method_type.description;
                let value = modal_payment_methods[ii].amount;
                bodyText += "<div class=\"dash-info bg-white\">\n" +
                    "            <div class=\"dash-info-start\"><span>" + label + "</span></div>\n" +
                    "            <div class=\"dash-info-spacing\"></div>\n" +
                    "            <div class=\"dash-info-end\"><span>" + value + "</span></div>\n" +
                    "        </div>";
            }

            service.confirmOrCancel({
                headerText: 'Raspoređivanje',
                bodyText: bodyText,
                confirmButtonText: 'Da, rasporedi',
                cancelButtonText: 'Odustani'
            }).then(function(result) {
                if (result.isConfirmed) {
                    invoice.payment_methods = modal_payment_methods;
                    invoice.is_cash = modal_payment_methods[0].payment_method_type.is_cash;
                    invoiceFactory.recalculatePaymentMethodTotals(invoice);
                }
            });
        });
    }

    function depositNeededModal() {
        return service.confirmOrCancel({
            headerText: 'Nije definisan depozit',
            bodyText: 'Za rad sa gotovinom morate definisati iznos dnevnog depozita. Da li želite da definišete iznos depozita sada?',
            confirmButtonText: 'Da, povedi me',
            cancelButtonText: 'Kasnije'
        })
    }

    function invalidForm() {
        return service.confirm({
            headerIcon: 'fa fa-exclamation-circle text-danger',
            headerText: 'Greška',
            bodyText: 'Podaci nisu ispravno popunjeni. Ispravite greške pa pokušajte ponovo.'
        });
    }

    function certificateUpload() {
        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/certificate-upload-modal/certificate-upload-modal.template.html',
            controller: 'CertificateUploadModalController',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            windowTemplateUrl: 'app/modals/window-fixed.template.html'
        });

        return modalInstance.result;
    }

    // -----------------------------------------------------------------------------------------------------------------
    // Internal modals
    // -----------------------------------------------------------------------------------------------------------------

    function paymentMethodPicker(initialData) {
        initialData = initialData !== undefined ? initialData : {};
        initialData.isMultiselect = initialData.isMultiselect !== undefined
            ? initialData.isMultiselect
            : false;
        initialData.selectedItems = initialData.selectedItems !== undefined
            ? angular.copy(initialData.selectedItems)
            : [];
        initialData.compare = (a, b) => { return a.id === b.id };

        initialData.title = 'Načini plaćanja';

        let TAB_CASH = 'Gotovinski';
        let TAB_NONCASH = 'Bezgotovinski';
        initialData.tabs = [];

        if (initialData.showCashTab === undefined || initialData.showCashTab === null) {
            initialData.showCashTab = true;
        }
        if (initialData.showCashTab) {
            initialData.tabs.push(TAB_CASH);
        }

        if (initialData.showNonCashTab === undefined || initialData.showNonCashTab === null) {
            initialData.showNonCashTab = true;
        }
        if (initialData.showNonCashTab) {
            initialData.tabs.push(TAB_NONCASH);
        }

        initialData.tab = initialData.tabs[0];

        initialData.searchEnabled = false;

        initialData.getItems = function(query, pageNumber, tab) {
            let newItems = [];
            if (tab === TAB_CASH) {
                newItems = fisConfig.filterPaymentMethods(query, true);
            } else if (tab === TAB_NONCASH) {
                newItems = fisConfig.filterPaymentMethods(query, false, true);
            } else {
                throw Error('Invalid tab');
            }

            return $q.resolve({
                items: newItems,
                totalItems: newItems.length
            });
        }

        let modalInstance = $uibModal.open({
            templateUrl: 'app/modals/payment-method-select-modal/payment-method-select-modal.template.html',
            controller: 'PaymentMethodSelectModal',
            controllerAs: 'ctrl',
            size: 'md',
            backdrop: 'static',
            // windowTemplateUrl: 'app/modals/window-fixed.template.html',
            windowTemplateUrl: 'app/modals/window-fullscreen.template.html',
            resolve: {
                initialData: initialData
            }
        });

        return modalInstance.result;
    }
}