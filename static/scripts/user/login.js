$(document).ready(
    onReady()
).keypress(function (e) {
    if (e.which == 13) {
        $("#submitLogin").submit();
    }
});
