angular
  .module("app")
  .controller(
    "OrderGroupCreateModalController",
    OrderGroupCreateModalController
  );

OrderGroupCreateModalController.$inject = ["$uibModalInstance", "api", "group"];

function OrderGroupCreateModalController($uibModalInstance, api, group) {
  let ctrl = this;
  ctrl.group = group;
  ctrl.isEdit = Boolean(group);
  if (ctrl.isEdit) {
    ctrl.group_id = ctrl.group.id;
    ctrl.name = group.naziv;
  } else {
    ctrl.name = "";
    ctrl.group_id = null;
  }

  ctrl.confirm = confirm;

  function confirm() {
    let action = "create";
    if (ctrl.isEdit) action = "edit";

    api.order_groups[action](ctrl.name, ctrl.group_id).then((res) => {
      $uibModalInstance.close({
        isConfirmed: true,
        group: res,
      });
    });
  }
}
