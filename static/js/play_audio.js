let main_table = document.getElementById('tbody_words');
let audio = document.getElementsByClassName('fa-volume-up');
let appropriate_voices = [];
window.speechSynthesis.onvoiceschanged = function() {
    let voices = window.speechSynthesis.getVoices();
    appropriate_voices = voices.filter(word => word.lang === "en-US" || word.lang === "en-GB");
}

for (let i=0; i<audio.length; i++){
    audio[i].addEventListener('click', function (){
        play_voice(main_table.rows[i].children[1].innerHTML);
    });
}

function play_voice(word) {
    function clean_word(word){
        return word.replace('/', ',')
    }
    let synth = window.speechSynthesis,
    message = new SpeechSynthesisUtterance();
    message.lang = 'en-US';
    message.text = clean_word(word);
    message.voice = appropriate_voices[0];
    message.rate = 0.9;
    synth.speak(message);
}