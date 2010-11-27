(function($) {
     function new_game() {
         console.log("Getting new game");
         $.ajax({url: $(this).attr('action'),
                 type: $(this).attr('method'),

                 success: function(data, text_status, xhr) {
                     console.log("We win:", data, text_status, xhr, xhr.getResponseHeader('location'));
                     window.location.hash = xhr.getResponseHeader('location').replace(/^\//, '#');
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
         var form_data = {};
         $($(this).serializeArray()).each(function(i, v) {
                                              form_data[v.name] = v.value;
                                          });
         var url = $(this).attr('action').replace('{game}', form_data['game-id']).replace(/^\//, '#');
         window.location.hash = url;

         return false;
     }

     $(function() {
           $('form#new-game').submit(new_game);
           $('form#go-to-game').submit(load_game);
     });
})(jQuery);