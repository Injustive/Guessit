let stats_icons = $('.stat_icon')

for (let i=0; i<stats_icons.length; i++){
    stats_icons[i].addEventListener('click', () => {
        show_stat(main_table.rows[i].firstElementChild.innerHTML);
    });
}


function show_stat(word_id) {
    let Statistic_w = undefined;

    function get_stat_from_server() {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: "GET",
                data: {'word_id': word_id},
                url: get_stat_url,
                dataType: "json",
                success: function (data) {
                    let stat = data['stat'];
                    let word_dates_stat = data['word_dates_stat'];
                    let res = [stat, word_dates_stat];
                    resolve(res)
                },
                error(data) {
                    console.log(data);
                }
            });
        });
    }

    function show_stat(){
        let preloader = $('.preloader_stat');
        let loader = preloader.find('.preloader__loader_stat');
        let card = $('.card-f');
        card.show();
        preloader.show();
        loader.show();
        card.dimBackground();
        $('#close_modal_stat').click(() => {
            card.hide();
            $.undim();
            for (let plot of Statistic_w.get_plots()){
                plot.destroy();
            }
        });
    }

    get_stat_from_server().then((res) => {
        let stat = res[0];
        let word_dates_stat = res[1];
        Statistic_w = new Statistics(stat, word_dates_stat);
        show_stat();
        return Statistic_w.plot();
    }).then(() => {
        let $preloader = $('.preloader_stat'),
        $loader = $preloader.find('.preloader__loader_stat');
		$loader.fadeOut();
		$preloader.delay(250).fadeOut(200);
    });
}