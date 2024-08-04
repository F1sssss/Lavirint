angular
  .module("app")
  .controller(
    "OrderGroupCreateModalController",
    OrderGroupCreateModalController
  );

OrderGroupCreateModalController.$inject = ["$uibModalInstance", "group"];

function OrderGroupCreateModalController($uibModalInstance, group) {
  let ctrl = this;
  ctrl.group = group;
  ctrl.isEdit = Boolean(group);

  if (ctrl.isEdit) ctrl.name = group.naziv;
  else ctrl.name = "";

  ctrl.confirm = confirm;

  function confirm() {
    $uibModalInstance.close({
      isConfirmed: true,
      group: { id: 10000, naziv: ctrl.name },
    });
  }
}
