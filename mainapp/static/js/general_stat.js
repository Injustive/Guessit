class Stat {
    constructor(stat) {
        this.stat = stat;
    }
    getPreviousMonthsDays(format){
        let days = [];

        for (let i = 0; i < 30; i++) {
            let day = moment().subtract(i, 'days').format(format);
            days.push(day);
        }
        return days;
    }
    get_data_charts(stat_fields){
        let getPreviousMonthsDays = this.getPreviousMonthsDays;
        let stat = this.stat

        function make_map() {
            let fields_data = [];
            for (let chart_field of stat_fields){
                let chart_field_map = new Map();
                for (let field of stat){
                    let date = moment(field['date']).format("D.MM.YY");
                    chart_field_map.set(date, field[chart_field]);
                }
                fields_data.push(chart_field_map);
            }
            return fields_data
        }
        function make_arr(maps){
            let res = [];
            for (let map_elem of maps){
                let data = []
                for (let day of getPreviousMonthsDays("D.MM.YY")){
                    if (map_elem.has(day)){
                    data.push(map_elem.get(day));
                    }
                    else {
                        data.push(0);
                    }
                }
                res.push(data)
            }
            return res;
        }
        return make_arr(make_map())
    }

    plot(canvas_id, stat_fields, settings, legend){
        let getPreviousMonthsDays = this.getPreviousMonthsDays;
        let stat = this.get_data_charts(stat_fields);
        let datasets = [];
        for (let i=0; i<stat.length; i++) {
            datasets.push(
                new Object({
                    label: settings[i]['label'],
                    borderColor:  settings[i]['borderColor'],
                    data: stat[i],
                    lineTension: 0.3,
                    pointBorderColor: 'black',
                    pointBackgroundColor: settings[i]['pointBackgroundColor']
                })
            );
        }

        new Chart(document.getElementById(canvas_id), {
            type: 'line',
            data: {
                labels: getPreviousMonthsDays('D.MM'),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        ticks: {
                            stepSize: 1,
                        },
                        beginAtZero: true,
                        suggestedMax: 5
                    },
                },
                plugins: {
                    legend: {
                    position: 'top',
                    },
                  title: {
                    display: true,
                    text: legend
                  }
                }
            }
        });
    }
}
const all_answers_settings = [
    {
        label: "Все",
        borderColor: "purple",
        pointBackgroundColor: 'purple'
    },
]
const c_r_answers_settings = [
    {
        label: '✓',
        borderColor: "#7fff00",
        pointBackgroundColor: '#7fff00'
    },
    {
        label: '✘',
        borderColor: "#ff0000",
        pointBackgroundColor: "#ff0000"
    }
]
const n_l_answers_settings = [
    {
        label: 'Новых',
        borderColor: "#ffa500",
        pointBackgroundColor: '#ffa500'
    },
    {
        label: 'Выучено',
        borderColor: "#ace1af",
        pointBackgroundColor: "#ace1af"
    }
]

let general_stat_url = $('#general_stat_input').attr('data-general-stat-url');

function plot_general_stat(){
    function get_general_stat(){
        return new Promise((resolve, reject) => {
            $.ajax({
                type: "GET",
                url: general_stat_url,
                success: function (data) {
                    let stat = data['results'];
                    resolve(stat);
                },
                error(data) {
                    console.log(data);
                }
            });
        });
    }

    get_general_stat().then((general_stat) => {
        let all_answers_chart = new Stat(general_stat);
        all_answers_chart.plot(
            "all_answers_chart",
            ['all_words'],
            all_answers_settings,
            "Количество карточек в день"
        );

        let c_r_answers_chart = new Stat(general_stat);
        c_r_answers_chart.plot(
            "c_i_answers_chart",
            ['correct_answers', 'incorrect_answers'],
            c_r_answers_settings,
            "Статистика правильных и неправильных ответов"
        );

        let n_l_charts = new Stat(general_stat);
        n_l_charts.plot(
            'n_l_charts',
            ['new_words', 'learned_words'],
            n_l_answers_settings,
            "Статистика новых и выученых слов"
        );
    })
}

plot_general_stat();
