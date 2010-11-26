window.gogogo = {
    query: undefined,
    boot: function($) {
        window.gogogo.query = $;
        $.ajaxSetup({
                        async: true,
                        contentType: 'application/json',
                        dataType: 'json'
                    });
        $(window).resize(window.gogogo.size_screen);
        $(window).bind('hashchange', gogogo.hash_change);
        $(window).trigger('hashchange');
    },

    hash_change: function(e) {
        var that = $(this);
        var frag_url = '/' + e.fragment;
        $('form[method=GET]').each(function(i, v) {
                                       var node = $(v),
                                           action = node.attr('action');
                                       var search = action.replace(/{.+?}/g, '(.+?)'),
                                           template = action.replace(/{.+?}/g, '{replace}');
                                       var found = frag_url.match(search);
                                       if(found) {
                                           $(found.slice(1)).each(function(i, v) {
                                                                      console.log("Replacement:", v);
                                                                      template = template.replace('{replace}', v);
                                           });
                                           console.log(i, "=>", node, "=>", action, "=>", search, found);
                                           console.log("Generated:", template);
                                           window.gogogo.load_board(template);
                                           window.gogogo.show_screens();
                                       }
        });
    },

    show_screens: function() {
        var $ = window.gogogo.query;

        $('.screen').removeClass('visible');

        if(window.location.hash)
            $('.screen' + window.location.hash.split('/')[0]).addClass('visible');
        else
            window.location.hash = $('.screen.default').attr('id');

        if($('.screen.visible').length == 0)
            $('.screen.default').addClass('visible');

        window.gogogo.size_screen();
    },

    size_screen: function() {
        var $ = window.gogogo.query;
        var screen = $('.screen.visible:first');
        var x = $(window).width(),
            y = $(window).height(),
            cx = Math.round(x * 0.8),
            cy = Math.round(y * 0.8);
        if(cx < 500) cx = 500;
        if(cy < 500) cy = 500;
        var ox = (x - cx) / 2.0,
            oy = (y - cy) / 2.0;
        screen.width(cx).height(cy).offset({top: oy, left: ox});
    }
};

(function($) {
     $(function() {
           window.gogogo.boot($);
     });
})(jQuery);
