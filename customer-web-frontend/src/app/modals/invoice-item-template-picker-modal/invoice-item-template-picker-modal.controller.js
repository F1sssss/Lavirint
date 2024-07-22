angular
    .module('app')
    .controller('InvoiceItemTemplatePickerModalController', InvoiceItemTemplatePickerModalController);

InvoiceItemTemplatePickerModalController.$inject = [
    '$uibModalInstance', '$timeout', 'api', 'fisConfig', 'breakpointsService'];

function InvoiceItemTemplatePickerModalController(
    $uibModalInstance, $timeout, api, fisConfig, breakpointsService) {
    let ctrl = this;

    ctrl.query = '';
    ctrl.isLoading = false;
    ctrl.pageNumber = 1;
    ctrl.total_items = 0;
    ctrl.invoiceItemTemplates = [];
    ctrl.isLoadMoreVisible = false;
    ctrl.selected = null;

    ctrl.loadPage = loadPage;
    ctrl.search = search;
    ctrl.searchOnInputEnter = searchOnInputEnter;
    ctrl.toggle = toggle;
    ctrl.confirm = confirm;

    // -----------------------------------------------------------------------------------------------------------------

    loadPage(1);

    // -----------------------------------------------------------------------------------------------------------------

    function loadPage(pageNumber) {
        let searchParameters = {
            pojam_za_pretragu: ctrl.query,
            broj_stranice: pageNumber,
            broj_stavki_po_stranici: 50
        }

        ctrl.isLoading = true;
        ctrl.isLoadMoreVisible = false;

        return api.magacin.poId.zalihe.listaj(fisConfig.user.magacin_id, searchParameters).then(function (data) {
            ctrl.invoiceItemTemplates = ctrl.invoiceItemTemplates.concat(data.stavke);
            ctrl.total_items = data.ukupan_broj_stavki;
            ctrl.isLoadMoreVisible = ctrl.invoiceItemTemplates.length < ctrl.total_items;
        }).finally(function () {
            ctrl.isLoading = false;
        });
    }

    function search() {
        ctrl.invoiceItemTemplates = [];
        loadPage(1);
    }

    function searchOnInputEnter($event) {
        if ($event.keyCode === 13) {
            ctrl.search()

            if (breakpointsService.ls(breakpointsService.keys.md)) {
                $event.target.blur();
            }
        }
    }

    function toggle(invoiceItemTemplate) {
        if (ctrl.selected === invoiceItemTemplate.id) {
            ctrl.selected = null
        } else {
            ctrl.selected = invoiceItemTemplate;
        }
    }

    function confirm() {
        $uibModalInstance.close({isConfirmed: true, invoiceItemTemplate: ctrl.selected})
    }
}