angular
    .module('app')
    .controller('PaymentMethodSelectModal', PaymentMethodSelectModal);

PaymentMethodSelectModal.$inject = [
    '$uibModalInstance', '$compile', '$templateRequest', 'fisConfig', 'initialData', 'fisModal'];

function PaymentMethodSelectModal(
    $uibModalInstance, $compile, $templateRequest, fisConfig, initialData, fisModal) {
    let ctrl = this;

    ctrl.searchEnabled = initialData.searchEnabled !== undefined ? initialData.searchEnabled : true;
    ctrl.title = initialData.title;
    ctrl.isLoading = false;
    ctrl.isMultiselect = initialData.isMultiselect || false;
    ctrl.selectedItems = initialData.selectedItems || [];
    ctrl.query = initialData.query || '';
    ctrl.templateUrl = initialData.templateUrl;

    ctrl.items = [];
    ctrl.pageNumber = 0;
    ctrl.totalItems = 0;
    ctrl.hasMoreItems = false;

    ctrl.tab = initialData.tab || null;
    ctrl.tabs = initialData.tabs || [];

    ctrl.toggle = toggle;
    ctrl.confirm = confirm;
    ctrl.search = search;
    ctrl.onTabChange = onTabChange;
    ctrl.searchOnInputEnter = searchOnInputEnter;
    ctrl.loadMoreItems = loadMoreItems;
    ctrl.compare = initialData.compare || function (a, b) { return a.id === b.id};

    // -----------------------------------------------------------------------------------------------------------------

    search();

    function getItems() {
        ctrl.isLoading = true;
        ctrl.hasMoreItems = false;
        ctrl.pageNumber += 1;
        return initialData.getItems(ctrl.query, ctrl.pageNumber, ctrl.tab).then(function(result) {
            ctrl.items = ctrl.items.concat(result.items);
            ctrl.totalItems = result.totalItems;
            ctrl.hasMoreItems = ctrl.items.length < ctrl.totalItems;
            update_selection(ctrl.items, ctrl.selectedItems, ctrl.compare);
        }).finally(function() {
            ctrl.isLoading = false;
        });
    }

    function search() {
        ctrl.items = [];
        ctrl.pageNumber = 0;
        getItems();
    }

    function onTabChange() {
        // ctrl.selectedItems.forEach(function(x) {
        //     x.is_selected = false;
        // });
        // ctrl.selectedItems = [];
        ctrl.search();
    }

    function searchOnInputEnter($event) {
        if ($event.keyCode === 13) {
            ctrl.search()

            if (breakpointsService.ls(breakpointsService.keys.md)) {
                $event.target.blur();
            }
        }
    }

    function loadMoreItems($event) {
        let modalWindow = angular.element($event.currentTarget).parents('.modal')[0];
        $(modalWindow).animate({ scrollTop: modalWindow.scrollHeight });
        getItems();
    }

    function update_selection(items, selected, compareFn) {
        for (let ii = 0; ii < items.length; ii++) {
            let item = items[ii];

            let selected_item = selected.find(function(x) {
                return compareFn(x, item);
            });

            item.is_selected = selected_item !== undefined;
        }
    }

    function toggle(payment_method_type) {
        _toggle(ctrl.selectedItems, payment_method_type, ctrl.isMultiselect, ctrl.compare);
    }

    function _toggle(selected_items, item, isMultiselect, compareFn) {
        let index = selected_items.findIndex(function(selectedItem) {
            return compareFn(selectedItem, item);
        });

        if (isMultiselect) {
            if (index >= 0) {
                item.is_selected = false;
                selected_items.splice(index, 1);
            } else {
                item.is_selected = true;
                selected_items.push(item);
            }
        } else {
            if (index >= 0) {
                item.is_selected = false;
                selected_items.splice(0, 1);
            } else {
                if (selected_items.length > 0) {
                    selected_items[0].is_selected = false;
                    selected_items.splice(0, 1);
                }
                item.is_selected = true;
                selected_items.push(item);
            }
        }
    }

    function confirm() {
        if (ctrl.selectedItems.length === 0) {
            fisModal.confirm({
                headerText: 'Greška',
                headerIcon: 'fa fa-exclamation-triangle text-danger',
                bodyText: initialData.isMultiselect
                    ? 'Morate odabrati makar jednu stavku.'
                    : 'Morate odabrati stavku.'
            });
            return;
        }

        ctrl.selectedItems.sort(function(a, b) {
            return a.id - b.id;
        });

        ctrl.selectedItems.forEach(function(x) {
            delete x.is_selected;
        });

        $uibModalInstance.close({
            isConfirmed: true,
            items: ctrl.selectedItems
        });
    }
}
