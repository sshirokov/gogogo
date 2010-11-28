(function($) {
     var fonts = '/static/js/fonts/fonts.json';
     var we = $('script:last');
     $.ajax({url: fonts, type: 'GET', async: false,
             error: function() { console.log("Error loading fonts", arguments); },
             success: function(data) {
                 data.fonts.forEach(function(font) {
                                        var path = data.base + font;
                                        we.after(
                                            $(document.createElement('script')).attr(
                                                {
                                                    type: 'application/javascript',
                                                    src: path
                                                })
                                        );
                 });
             }
     });
})(jQuery);