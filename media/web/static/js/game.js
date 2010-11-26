(function($) {
     function new_game() {
         console.log("Getting new game");
         $.ajax({url: $(this).attr('action'),
                 type: $(this).attr('method'),

                 success: function(data, text_status, xhr) {
                     console.log("We win:", data, text_status, xhr, xhr.getResponseHeader('location'));

                     return false;
                 },

                 error: function(xhr, text_status, errorThrown) {
                     console.log("We lose:", xhr, text_status, errorThrown);

                     return false;
                 }
         });

         return false;
     }

     function load_game() {
         console.log("Loading game");

         return false;
     }
     $(function() {
           $('form#new-game').submit(new_game);
           $('form#go-to-game').submit(load_game);
     });
})(jQuery);