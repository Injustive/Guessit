let input = document.getElementById('search_form_input');
let words_type = document.getElementById("words_type");
let form_action_url = document.forms.search_form.action;
let data = {};
data['words_type'] = words_type.attributes.value.value;
input.addEventListener('input', function (){
    if (this.value.length >= 2) {
        data['word'] = this.value;
        $.ajax({
            type:"GET",
            url: form_action_url,
            dataType:"json",
            data: data,
            success: function (data) {
                if (data){
                   $('#drp_dwn_ul_search').html(data);
                }
                else {
                    $('#drp_dwn_ul_search').empty();
                }

            },
            error: function (data){
                console.log(data);
            }
        });
    }
    else {
        $('#drp_dwn_ul_search').empty();
    }
});