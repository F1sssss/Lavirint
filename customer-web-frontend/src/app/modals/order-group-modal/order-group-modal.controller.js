angular
    .module('app')
    .controller('OrderGroupModalController', OrderGroupModalController);

OrderGroupModalController.$inject = ['$uibModalInstance', "groups"];

function OrderGroupModalController($uibModalInstance, groups) {
    let ctrl = this;
    ctrl.group = "";
    ctrl.groups = groups;
}