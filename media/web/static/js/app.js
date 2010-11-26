window.gogogo = {
    query: undefined,
    boot: function($) {
        window.gogogo.query = $;
        $.ajaxSetup({
                        contentType: 'application/json',
                        dataType: 'json'
                    });
    },

    show_screens: function() {
        var $ = window.gogogo.query;

        $('.screen').removeClass('visible');

        if(window.location.hash)
            $('.screen' + window.location.hash).addClass('visible');
        else
            window.location.hash = $('.screen.default').attr('id');

        if($('.screen.visible').length == 0)
            $('.screen.default').addClass('visible');
    }
};

(function($) {
     $(function() {
           window.gogogo.boot($);
           window.gogogo.show_screens();
     });
})(jQuery);
