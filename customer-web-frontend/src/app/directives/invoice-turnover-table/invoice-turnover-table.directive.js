angular
    .module('app')
    .directive('invoiceTurnoverTable', invoiceTurnoverTable);

invoiceTurnoverTable.$inject = [];

function invoiceTurnoverTable() {
    return {
        restrict: 'E',
        templateUrl: 'app/directives/invoice-turnover-table/invoice-turnover-table.template.html',
        link: link,
        scope: {
            creditNote: '=',
            viewInvoices: '=invoices',
            selectedInvoices: '=',
            selectionChanged: '&'
        }
    }

    function link($scope, $element, $attributes, $controllers) {
        $scope.toggle = toggle;

        $scope.selectedIds = [];

        function toggle(invoice) {
            let index = $scope.selectedIds.indexOf(invoice.id);
            let isSelected = index >= 0;

            doSelectMultiple();

            function doSelectMultiple() {
                if (isSelected) {
                    let event = { shouldSelect: true };
                    $scope.selectionChanged({ 'action': 'remove', invoice: invoice, selectedInvoices: $scope.selectedInvoices, selectedIds: $scope.selectedIds, event: event }).then(function() {
                        if (event.shouldSelect) {
                            $scope.selectedIds.splice(index, 1);
                            if ($scope.selectedInvoices) {
                                $scope.selectedInvoices.splice(index, 1);
                            }
                        }
                    });
                } else {
                    let event = { shouldSelect: true };
                    $scope.selectionChanged({ 'action': 'add', invoice: invoice, selectedInvoices: $scope.selectedInvoices, selectedIds: $scope.selectedIds, event: event }).then(function() {
                        if (event.shouldSelect) {
                            $scope.selectedIds.push(invoice.id);
                            if ($scope.selectedInvoices) {
                                $scope.selectedInvoices.push(invoice);
                            }
                        }
                    });
                }
            }
        }
    }
}