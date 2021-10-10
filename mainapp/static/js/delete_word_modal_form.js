let table = document.getElementById('tbody_words');
for (let i=0; i<table.rows.length; i++){
    table.rows[i].lastElementChild.children[3].children[0].addEventListener('click', () => {
        let modal_form = table.rows[i].lastElementChild.children[4]
        delete_modal_form(modal_form);
    });
}

function delete_modal_form(modal_form){
    modal_form.style = 'display: block';
    $(modal_form).dimBackground();
    modal_form.getElementsByClassName('close_modal_form')[0].addEventListener('click', () => {
        modal_form.style = 'display: none'
        $.undim();
    });
}