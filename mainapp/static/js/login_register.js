function show() {
    var p = document.getElementById('pwd');
    p.setAttribute('type', 'text');
}

function hide(elem) {
    var p = document.getElementById('pwd');
    p.setAttribute('type', 'password');
}
var pwShown = 0;

eye = document.getElementById("eye")
if (eye) {
    eye.addEventListener("click", function () {
        if (pwShown == 0) {
            pwShown = 1;
            show();
        } else {
            pwShown = 0;
            hide();
        }
    }, false);
}



function show2() {
    var p = document.getElementById('pwd2');
    p.setAttribute('type', 'text');
}

function hide2() {
    var p = document.getElementById('pwd2');
    p.setAttribute('type', 'password');
}

eye2 = document.getElementById("eye2")
if (eye2) {
    eye2.addEventListener("click", function () {
        if (pwShown == 0) {
            pwShown = 1;
            show2();
        } else {
            pwShown = 0;
            hide2();
        }
    }, false);
}