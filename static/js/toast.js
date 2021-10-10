
let elem = document.getElementsByClassName("toast")[0];
if (elem) {
    elem.className = elem.className + " show";
    setTimeout(function(){ elem.className = elem.className.replace("show", ""); }, 3000);
}

