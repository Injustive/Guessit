let stats_icons = $('.stat_icon')

for (let i=0; i<stats_icons.length; i++){
    stats_icons[i].addEventListener('click', () => {
        let stat_url = $(stats_icons[i]).attr('data-stat-url');
        let dates_stat_url = $(stats_icons[i]).attr('data-dates-stat-url');
        show_stat(stat_url, dates_stat_url);
    });
}


function show_stat(stat_url, dates_stat_url) {
    let Statistic_w = undefined;

    function get_word_stat_from_server() {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: "GET",
                url: stat_url,
                success: function (data) {
                    let stat = data['stat'];
                    resolve(stat);
                },
                error(data) {
                    console.log(data);
                }
            });
        });
    }

    function get_word_dates_stat_from_server(){
        return new Promise((resolve, reject) => {
             $.ajax({
                type: "GET",
                url: dates_stat_url,
                success: function (data) {
                    let results = data['results'];
                    resolve(results);
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

    Promise.all(
        [get_word_stat_from_server(),
        get_word_dates_stat_from_server()]
        ).then(values => {
            let stat = values[0][0];
            let word_dates_stat = values[1];
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