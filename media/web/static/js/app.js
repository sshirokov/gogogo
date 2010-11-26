window.gogogo = {
    query: undefined,
    boot: function($) {
        $.ajaxSetup({
                        contentType: 'application/json',
                        dataType: 'json'
                    });
        window.gogogo.query = $;
    }
};

(function($) {
     $(function() {
           window.gogogo.boot($);
     });
})(jQuery);
