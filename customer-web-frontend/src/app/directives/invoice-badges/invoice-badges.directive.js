angular
    .module('app')
    .directive('invoiceBadges', invoiceBadges);

invoiceBadges.$inject = [];

function invoiceBadges() {
    return {
        restrict: 'E',
        replace: true,
        link: link,
        templateUrl: 'app/directives/invoice-badges/invoice-badges.template.html',
        scope: {
            invoice: '=invoice'
        }
    }

    function link($scope, $element, $attributes) {
        $scope.badges = [];

        if ($scope.invoice.tip_fakture_id === 1) {
            $scope.badges.push({
                text: 'redovni račun',
                class: 'bg-dark'
            });
        }

        if ($scope.invoice.advance_invoice_id !== undefined && $scope.invoice.advance_invoice_id !== null) {
            $scope.badges.push({
                text: 'konačni račun',
                class: 'bg-danger'
            });
        }

        if ($scope.invoice.tip_fakture_id === 2) {
            $scope.badges.push({
                text: 'storno račun',
                class: 'bg-primary'
            });
        }

        if ($scope.invoice.tip_fakture_id === 5 || $scope.invoice.is_advance_invoice) {
            $scope.badges.push({
                text: 'avans',
                class: 'bg-info'
            });
        }

        if ($scope.invoice.tip_fakture_id === 3) {
            $scope.badges.push({
                text: 'zbirni račun',
                class: 'bg-info'
            });
        }

        if ($scope.invoice.status === 5) {
            $scope.badges.push({
                text: 'ima knjižno odobrenje',
                class: 'bg-info'
            });
        }

        if ($scope.invoice.tip_fakture_id === 7) {
            $scope.badges.push({
                text: 'korektivni račun',
                class: 'bg-primary'
            });
        }

        if ($scope.invoice.tip_fakture_id === 8) {
            $scope.badges.push({
                text: 'ispravka greške',
                class: 'bg-secondary'
            });
        }

        if ($scope.invoice.status === 4) {
            $scope.badges.push({
                text: 'storniran',
                class: 'bg-danger'
            });
        }

        if ($scope.invoice.status === 6) {
            $scope.badges.push({
                text: 'ispravljen',
                class: 'bg-secondary'
            });
        }

        if ($scope.invoice.je_korigovana) {
            $scope.badges.push({
                text: 'korigovan',
                class: 'bg-warning'
            });
        }

        if ($scope.invoice.status === 1 || $scope.invoice.status === 3) {
            $scope.badges.push({
                text: 'neuspjela fiskalizacija',
                class: 'bg-danger'
            });
        }

        if ($scope.invoice.tip_fakture_id === 9) {
            $scope.badges.push({
                text: 'predračun',
                class: 'bg-secondary'
            })
        }
    }
}