class Statistics {

    constructor(stat, word_dates_stat) {
        this.stat = stat;
        this.PieChart = undefined;
        this.LineChart = undefined;
        this.word_dates_stat = word_dates_stat;
    }

    plot() {
        return new Promise((resolve, reject) => {
        let stat = this.stat;
        let word_dates_stat = this.word_dates_stat;

        $('#lvl_progress').html(stat.memorise_lvl + '/6');
        $('#correct_answers_row').html(stat.correct_answers_in_a_row);
        $('#coeff_progress').html(stat.memorise_coefficient + '/4');
        $('#created_at').html(moment(stat.created_at).format('D-MM-YYYY'));

        function getPreviousMonthsDays(format) {
            let days = [];

            for (let i = 0; i < 30; i++) {
                let day = moment().subtract(i, 'days').format(format);
                days.push(day);
            }
            return days;
        }

        function get_data(){


            function make_map(field) {
                let res = new Map();
                if (field==='sum'){
                    for (let stat of word_dates_stat){
                        let date = moment(stat['date']).format("D.MM.YY");
                        res.set(date, stat['correct_answers'] + stat['incorrect_answers'])
                    }
                    return res
                }
                for (let stat of word_dates_stat){
                    let date = moment(stat['date']).format("D.MM.YY");
                    res.set(date, stat[field])
                }
                return res
            }

            function make_arr(map){
                let res = [];
                for (let day of getPreviousMonthsDays("D.MM.YY")){
                    if (map.has(day)){
                        res.push(map.get(day));
                    }
                    else {
                        res.push(0);
                    }
                }
                return res;
            }

            let correct_answers_m = make_map('correct_answers');
            let incorrect_answers_m = make_map('incorrect_answers');
            let all_answers = make_map('sum');

            let all_data = make_arr(all_answers);
            let correct_answers_data = make_arr(correct_answers_m);
            let incorrect_answers_data = make_arr(incorrect_answers_m);


            return [all_data, correct_answers_data, incorrect_answers_data];
        }

       this.PieChart = new Chart(document.getElementById("pie-chart"), {
            type: 'pie',
            data: {
                datasets: [{
                    backgroundColor: ["lightgreen", "#FF7276"],
                    data: [stat['correct_answers'], stat['incorrect_answers']]
                }],
                labels: ["✓", "✘"],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        color: 'black',
                        text: `Всего ответов: ${stat.incorrect_answers+stat.correct_answers}`,
                        padding: {
                            top: 5,
                            bottom: 0
                        },
                        font: {
                            size: 14,
                        }
                    },
                },
                animation: {
                    onComplete: function(e) {
                      resolve();
                    }
                }
            },
        });

        this.LineChart = new Chart(document.getElementById("date-chart"), {
            type: 'line',
            data: {
                labels: getPreviousMonthsDays('D.MM'),
                datasets: [{
                    label: 'Все',
                    borderColor: "purple",
                    data: get_data()[0],
                    lineTension: 0.3,
                    pointBorderColor: 'black',
                    pointBackgroundColor: 'purple',
                },
                {
                    label: '✓',
                    borderColor: "#7fff00",
                    data: get_data()[1],
                    lineTension: 0.3,
                    pointBorderColor: 'black',
                    pointBackgroundColor: '#7fff00',
                },
                {
                    label: '✘',
                    borderColor: "#ff0000",
                    data: get_data()[2],
                    lineTension: 0.3,
                    pointBorderColor: 'black',
                    pointBackgroundColor: '#ff0000',
                }]
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
                    }
                }
            }
            });
        });
    }

    get_plots() {
        return [this.PieChart, this.LineChart];
    }

    destroy_plots(plots){
        for (let plot of plots) {
            plot.destroy();
        }
    }
}