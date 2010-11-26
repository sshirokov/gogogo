(function($) {
     function new_game() {
         console.log("Getting new game");

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