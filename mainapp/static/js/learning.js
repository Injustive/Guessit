let translation = document.getElementsByClassName('translation')[0];
let answer = document.getElementById('answer');
let form_send_answer = document.forms.form_send_answer;
let form_answer_div = document.getElementsByClassName('form-answer')[0];
let example_div_en = document.getElementsByClassName('example-en')[0];
let example_div_ru = document.getElementsByClassName('example-ru')[0];
let new_word = document.getElementById('new_word');
let word = undefined;
let tenses = undefined;
let csrf_token = form_send_answer.csrfmiddlewaretoken.value;
let is_correct = true;
let word_volume = document.getElementById('word-volume');
let sentence_volume = document.getElementById('sentence-volume');
let timbre = document.getElementById('timbre');
let voiceSelect = document.querySelector('select');
let stat = undefined;
let Statistic_w = undefined;

const getVoices = () => {
  return new Promise(resolve => {
    let voices = speechSynthesis.getVoices();
    if (voices.length) {
      resolve(voices);
      return
    }
    speechSynthesis.onvoiceschanged = () => {
      voices = speechSynthesis.getVoices();
      resolve(voices);
    }
  })
}

const configure_voice_select = async () => {
    let voices = await getVoices();
    let appropriate_voices = voices.filter(voice => voice.lang === "en-US" || voice.lang === "en-GB");
    for(let i of appropriate_voices.reverse()) {
        var option = document.createElement('option');
        option.textContent = i.name + ' (' + i.lang + ')';
        option.setAttribute('data-lang', i.lang);
        option.setAttribute('data-name', i.name);
        voiceSelect.appendChild(option);
    }
}

configure_voice_select();

$(".setings-dropdown-content").hover(
    function () {
        $(".settings-icon").addClass('hovered');
    },
    function () {
        $(".settings-icon").removeClass("hovered");
    }
);

$('#back_to_inp').click(() => {
    $('.card-f').removeClass('is-flipped');
});
$('.card-f').contextmenu((e) =>{
    e.preventDefault();
    $('.card-f').toggleClass('is-flipped');
});

function lineBar_animate(progress) {
    var lineBar = new ProgressBar.Line("#progress", {
        strokeWidth: 4,
        trailWidth: 0.5,
        easing: 'easeIn',
        trailColor: '#808080',
        from: {color: "#ffff00"},
        to: {color: "#006400"},
        text: {
            value: '0',
            className: 'progress-text',
            style: {
                color: 'black',
                position: 'absolute',
                top: '-30px',
                padding: 0,
                margin: 0,
                transform: null,
            }
        },
        step: (state, shape) => {
            shape.path.setAttribute("stroke", state.color);
        }
    });

    lineBar.animate(progress, {
        duration: 800
    });
}

function get_ur_params() {
    let params = window
        .location
        .search
        .replace('?', '')
        .split('&')
        .reduce(
            function (p, e) {
                var a = e.split('=');
                p[decodeURIComponent(a[0])] = decodeURIComponent(a[1]);
                return p;
            },
            {}
        );
    return params
}

function get_width(text, font) {
    // re-use canvas object for better performance
    var canvas = document.createElement("canvas");
    var context = canvas.getContext("2d");
    context.font = font;
    var metrics = context.measureText(text);
    return metrics.width;
}

function get_word() {
    let promise = new Promise((resolve, reject) => {
        is_correct = true;
        $.ajax({
            type: "GET",
            data: get_ur_params(),
            url: form_send_answer.action,
            dataType: "json",
            success: function (data) {
                const percents = {
                    1: .15,
                    2: .35,
                    3: .5,
                    4: .65,
                    5: .8,
                    6: 1
                }
                stat = data['stat'];
                let word_dates_stat = data['word_dates_stat'];
                let stat_today = data['stat_today'];
                let progress = !stat ? 0 : percents[stat['memorise_lvl']];
                let is_learned = !stat ? undefined : stat['is_learned'];
                let new_words = !stat_today ? 0 : stat_today['new_words']
                let all_words = !stat_today ? 0 : stat_today['correct_answers'] + stat_today['incorrect_answers']
                tenses = data['tenses'];
                word = data['data'];

                $('#new_words_a').text(new_words);
                $('#all_words_a').text(all_words);
                answer_font = $('#answer').css('font')
                answer.style.width = get_width(word['word'], answer_font) + 'px';
                translation.innerHTML = word['translation'];
                lineBar_animate(progress)
                if (is_learned) {
                    $('#is_learned').show();
                }
                // console.log(word['word']);
                get_example(word);

                if (stat) {
                    Statistic_w = new Statistics(stat, word_dates_stat);
                    $('.no_stat').hide();
                    $('.stat').show();
                    Statistic_w.plot();
                }
                else {
                    $('.stat').hide();
                    $('.no_stat').show();
                    new_word.style.display = 'block';
                }
                resolve()
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
    return promise
}

function get_example(word) {
    let rusex = word['rusex'];
    let engex_arr = word['engex'].split(' ');
    let flag = false;
    for (let tense in tenses) {
        for (let engex in engex_arr) {
            temp = engex_arr[engex].replace(/[\s.,%!?']/g, '').toLowerCase();
            if (tenses[tense].toLowerCase() === temp) {
                engex_arr[engex] = `<span style='color: red'>${engex_arr[engex]}</span>`;
                flag = true;
            }
        }
    }
    let res = engex_arr.join(' ')
    if (!flag) {
        let r = "(" + word['word'] + ")";
        let reg = new RegExp(r, "g");
        res = res.replace(reg, "<span style='color: red'>$1</span>");
    }
    example_div_en.innerHTML = res;
    example_div_ru.innerHTML = rusex;
}

function submit_answer_form() {
    if (this.answer.value.toLowerCase() === word['word'].toLowerCase()) {
        action_after_answer('correct');
    } else {
        is_correct = false;
        action_after_answer('incorrect');
    }
}

function send_correct_or_incorrect_answer(is_correct) {
    $.ajax({
        type: "POST",
        url: form_send_answer.action,
        data: {
            csrfmiddlewaretoken: csrf_token,
            word_id: word['id'],
            is_correct: is_correct
        },
        dataType: "json",
        error: function (error) {
            console.log(error);
        }
    });
}

function play_voice(text, rate = 1.4, pitch=0.8, callback = undefined) {
    let clean_text = text.replace(/ *\([^)]*\) */g, "");
    let synth = window.speechSynthesis;
    let voices = synth.getVoices();
    let message = new SpeechSynthesisUtterance();
    message.lang = 'en-US';
    message.pitch = pitch;
    message.text = clean_text;
    message.rate = rate;
    message.onend = () => {
        if (callback) {
            callback();
        }
    }
    if (voiceSelect.length) {
        let selectedOption = voiceSelect.selectedOptions[0].getAttribute('data-name');
        for(let i = 0; i < voices.length ; i++) {
            if(voices[i].name === selectedOption) {
              message.voice = voices[i];
            }
        }
    }
    synth.speak(message)
}

function action_after_answer(cls) {
    if (cls === 'correct') {
        send_correct_or_incorrect_answer(is_correct);
    }

    function get_new_word(time = 1000) {
        let promise = new Promise((resolve, reject) => {
            setTimeout(function () {
                answer.style.color = '#037889';
                answer.value = '';
                answer.placeholder = '';
                answer.classList.remove(cls);
                resolve();
            }, time);
        });
        return promise
    }

    if (cls === 'correct') {
        if (!$("#example_skip_check").prop('checked')) {
            $('#skip_example').show();
        }
        $('#progress').empty();
        $(new_word).hide();
        $('#card-f.is-flipped').hide();
        $(".form-answer").hide();
        $('.daily_stat_icons').hide();
        $('#is_learned').hide();
        $('#chart_rotate_icon').hide();
        $(".example").show();
        play_voice(word['engex'], rate = sentence_volume.value, pitch = timbre.value, callback = function () {
            get_new_word(0).then(() => {
                return new Promise((resolve, reject) => {
                    if ($("#example_skip_check").prop('checked')){
                        resolve();
                    }
                    else{
                        $(document).keydown((e) => {
                            if(e.keyCode === 13) {
                                resolve();
                            }
                        });
                        $('#skip_example').click(() => {
                            resolve();
                        });
                    }
                });
            }).then(() => {
                if (Statistic_w){
                    let plots = Statistic_w.get_plots();
                    Statistic_w.destroy_plots(plots);
                }
                get_word().then(() => {
                    $('#skip_example').hide();
                    $(".example").hide();
                    $(".form-answer").show();
                    $('.daily_stat_icons').show();
                    $('#chart_rotate_icon').show();
                    answer.focus();
                });
            });
        });
    } else {
        play_voice(word['word'], rate = word_volume.value, pitch = timbre.value);
        this.answer.classList.add(cls);
        this.answer.value = '';
        this.answer.placeholder = word['word'];
        get_new_word();
    }
}

get_word().then(() => {
    $(function () {
        $('body').show();
    });
});




