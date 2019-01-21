$(document).ready(
    onReady()
);

function onReady() {
    let regMsg = $("#accountRegister"),
        icon = $("#accountAvailable"),
        parent = $("#accountIDParent");

    regMsg.hide();
    $("input[name=accountID]").focusout(function () {
        if ($(this).val() !== "") {
            // noinspection JSUnresolvedFunction
            // noinspection JSUnresolvedVariable
            $.getJSON(Flask.url_for("api.check_account_id_available", {"account_id": $(this).val()}), function (json) {
                let available = Boolean(Number(json));

                icon.removeClass("glyphicon-user");

                if (available) {
                    parent.removeClass("has-error").addClass("has-success");
                    icon.removeClass("glyphicon-remove").addClass("glyphicon-ok");
                    regMsg.hide();
                } else {
                    parent.removeClass("has-success").addClass("has-error");
                    icon.removeClass("glyphicon-ok").addClass("glyphicon-remove");
                    regMsg.show();
                }
            });
        } else {
            icon.removeClass("glyphicon-ok").removeClass("glyphicon-remove").addClass("glyphicon-user");
            regMsg.hide();
        }
    });
}