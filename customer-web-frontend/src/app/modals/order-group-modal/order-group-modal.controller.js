angular
  .module("app")
  .controller("OrderGroupModalController", OrderGroupModalController);

OrderGroupModalController.$inject = ["$uibModalInstance", "invoice"];

function OrderGroupModalController($uibModalInstance, invoice) {
  let ctrl = this;
  ctrl.group = "";
  ctrl.invoice = invoice;

  ctrl.confirm = confirm;

  function confirm() {
    $uibModalInstance.close({ isConfirmed: true, group: ctrl.group });
  }
}
