(function($) {
     function load_board(url) {
         console.log("Loading board from:", url);
         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     console.log("We win a board:", data, text_status, xhr, xhr.getResponseHeader('location'));

                     return false;
                 },

                 error: function(xhr, text_status, errorThrown) {
                     console.log("We lose:", xhr, text_status, errorThrown);

                     return false;
                 }
         });
     }
     //Create paper
     window.gogogo.paper = Raphael($('#game').get(0), 500, 500);
     var c = window.gogogo.paper.circle(250, 250, 50);
     c.attr('fill', "#ff0000");
     window.gogogo.load_board = load_board;
})(jQuery);