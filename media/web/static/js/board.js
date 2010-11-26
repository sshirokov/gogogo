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
     window.gogogo.load_board = load_board;
})(jQuery);