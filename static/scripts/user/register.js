$(document).ready(
    onReady()
).keypress(function (e) {
    if (e.which == 13) {
        $("#submitNewUser").submit();
    }
});

function initLayouts() {
    $(".after-usertype").hide();
    $(".phone-only, .email-only, .manual-only, .student-only").hide();
}

function onReady() {
    initLayouts();

    $(".idTypes").click(onIdTypesClicked);
    $(".notif").click(onNotifPrefClicked);

    $("#submitNewUser").submit(onFormSubmit);

    $("#langList").change(function () {
        onSelectChangedUpdateInput($(this), "#lang");
    });
    $("#carrierList").change(function () {
        onSelectChangedUpdateInput($(this), "#carrier");
    });

    inputVerify("api.check_account_id_available", "account_id", "accountID", "account-id-parent", "accountIDstatus");
    inputVerify("api.check_student_id_available", "student_id", "studentID", "student-id-parent", "studentIDstatus");
}

function inputVerify(endpoint, param_name, input_id, parent_input_id, glyphicon_id) {
    $("#" + input_id + "recov").hide();

    $("input[name=" + input_id + "]").focusout(function () {
        if ($(this).is(":visible") && $(this).not(":hidden")) {
            var elem = $("#" + glyphicon_id);
            var param_dict = {};
            param_dict[param_name] = $(this).val();

            if ($(this).val() !== "") {
                $.getJSON(Flask.url_for(endpoint, param_dict), function (json) {
                    var available = Boolean(Number(json));

                    elem.removeClass("glyphicon-user");

                    if (available) {
                        $("#" + parent_input_id).removeClass("has-error").addClass("has-success");
                        elem.removeClass("glyphicon-remove").addClass("glyphicon-ok");
                        $("#" + input_id + "recov").hide();
                    } else {
                        $("#" + parent_input_id).removeClass("has-success").addClass("has-error");
                        elem.removeClass("glyphicon-ok").addClass("glyphicon-remove");
                        $("#" + input_id + "recov").show();
                    }

                    changeSubmitButtonEnabled(available);
                });
            } else {
                elem.removeClass("glyphicon-ok").removeClass("glyphicon-remove").addClass("glyphicon-user");
                $("#" + input_id + "recov").hide();
            }
        }
    });
}

function changeSubmitButtonEnabled(enabled) {
    var submitBtn = $("#submit");

    if (enabled) {
        submitBtn.removeAttr("disabled");
    } else {
        submitBtn.attr("disabled", "disabled");
    }
}

function onSelectChangedUpdateInput(select, input) {
    $(input).val(select.find("option:selected").data("tokens").split("|")[1]);
}

function onIdTypesClicked(event) {
    $(".idTypes").addClass("btn-danger");
    $(event.target).removeClass("btn-danger").addClass("btn-success");
    $("#idType").val(event.target.value);
    $(".after-usertype").show();

    if ($(event.target).val() == 1) {
        $(".student-only").show();
        $("input[name=studentId]").attr("required", "required"); 
    } else {
        $(".student-only").hide();
        $("input[name=studentId]").removeAttr("required"); 
    }
}

function onNotifPrefClicked(event) {
    let target = $(event.target);
    let input_obj = $("#" + target.data("input"));
    let new_bool = !Boolean(Number(input_obj.val()));

    input_obj.val(Number(new_bool))

    if (new_bool) {
        target.removeClass("btn-danger").addClass("btn-success");
        $("." + target.data("type") + "-only").show();
    } else {
        target.removeClass("btn-success").addClass("btn-danger");
        $("." + target.data("type") + "-only").hide();
    }
}

function onFormSubmit() {
    let alertElem = $("#errMissingFields");
    let alertData = $("#dataMissingFields");

    let missing = [];

    let success = true;

    if ($("#idType").val() == 1) {
        if ($("#notifSMS").val() == 1) {
            if (!$("input[name=phoneNum]").val()) {
                $("#phone-num").addClass("has-error");
                missing.push("Phone Number");
                success = false;
            }
            if ($("#carrier").val() == "-") {
                missing.push("Phone Carrier");
                $("#phone-carrier").addClass("has-error");
                success = false;
            }
        }

        if ($("#notifEmail").val() == 1) {
            if (!$("input[name=studentEmail]").val()) {
                missing.push("Email");
                $("#email-input").addClass("has-error");
                success = false;
            }
        }

        if ($("#notifManual").val() == 1) {
            if (!$("input[name=namePron]").val()) {
                missing.push("Name Pronuncitation");
                $("#manual-pron").addClass("has-error");
                success = false;
            }
        }

        if ($("#lang").val() == -1) {
            missing.push("Language");
            $("#lang-parent").addClass("has-error");
            success = false;
        }
    }

    if (!success) {
        alertData.text(missing.join(", "));
        alertElem.removeClass("hide");
        $(window).scrollTop(0);
    }
    return success;
}

