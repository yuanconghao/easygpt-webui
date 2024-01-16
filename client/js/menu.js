$(function () {
    $('.easygpt_menu').popup();
    $('.easygpt_menu_home').click(function () {
        window.open('/easygpt/', '_self');
    });
    $('.easygpt_menu_asr').click(function () {
        window.open('/easygpt/asr/', '_blank');
    });
    $('.easygpt_menu_tts').click(function () {
        window.open('/easygpt/tts/', '_blank');
    });
    $('.easygpt_menu_prompt').click(function () {
        window.open('/easygpt/prompt/', '_blank');
    });
    $('.easygpt_menu_teacher').click(function () {
        window.open('/easygpt/teacher/', '_blank');
    });
    $('.easygpt_menu_corpus').click(function () {
        window.open('/easygpt/corpus/', '_blank');
    });
    $('.easygpt_menu_convert').click(function () {
        window.open('/easygpt/convert/', '_blank');
    });
});