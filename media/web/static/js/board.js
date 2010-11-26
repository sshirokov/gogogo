(function($) {
     var gfx = window._gfx = {
         paper: undefined,
         container: '#game',
         width: 500,
         height: 500,
         rows: 19,
         cols: 19,
         step: false,
         corner_offset: 30,

         elements: {

         }
     };

     function load_board(url) {
         console.log("Loading board from:", url);
         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     window.gogogo.draw_board();
                     console.log("We win a board:", data, text_status, xhr, xhr.getResponseHeader('location'));
                     if(data.over) {
                         $(".messages #player").html("Game Over");
                     }
                     else {
                         $(".messages #player").html(data.turn);
                     }
                     $(data.data.moves).each(function(i, v) {
                                                 console.log("Move:", v.player, v.passing, "(" + v.x + ",", v.y + ")");
                                                 if(!v.passing) {
                                                     gfx.elements.stones[v.player] = gfx.elements.stones[v.player] || [];
                                                     gfx.elements.stones[v.player].push(
                                                         gfx.paper.circle(gfx.corner_offset + (
                                                                              v.x * gfx.step
                                                                          ),
                                                                          gfx.corner_offset + (
                                                                              ((data.data.height - 1) - v.y) * gfx.step
                                                                          ),
                                                                          10)
                                                     );
                                                 }
                     });

                     return false;
                 },

                 error: function(xhr, text_status, errorThrown) {
                     console.log("We lose:", xhr, text_status, errorThrown);

                     return false;
                 }
         });
     }

     function draw_board(board) {
         gfx.paper.clear();
         gfx.elements = {};

         //Draw underling board
         gfx.elements.base = gfx.paper.rect(10, 10, 480, 480, 5);
         gfx.elements.base.attr('fill', "#D1D190");
         gfx.elements.lines = [];
         gfx.elements.stones = {};
         gfx.step = (gfx.width - (gfx.corner_offset * 2)) / (gfx.rows - 1);

         for(var col = 0; col < gfx.cols; col++) {
             var ex, ey,
                 sx = gfx.corner_offset,
                 sy = gfx.corner_offset,
                 distance = gfx.width - (sx * 2),
             ey = distance + sx;
             sx += (gfx.step * col);
             ex = sx;
             var path = "M" + sx + " " + sy + "L" + ex + " " + ey;
             gfx.elements.lines.push(gfx.paper.path(path));
         }

         for(var row = 0; row < gfx.rows; row++) {
             var ex, ey,
                 sx = gfx.corner_offset,
                 sy = gfx.corner_offset,
                 distance = gfx.width - (sy * 2),
                 step = distance / (gfx.rows - 1);
             ex = distance + sx;
             sy += (gfx.step * row);
             ey = sy;
             var path = "M" + sx + " " + sy + "L" + ex + " " + ey;
             gfx.elements.lines.push(gfx.paper.path(path));
         }

     }

     //Unpublished
     function init_board() {
         //Create paper
         gfx.paper = Raphael($(gfx.container).get(0), gfx.width, gfx.height);

     }

     //Publish and API
     window.gogogo.load_board = load_board;
     window.gogogo.draw_board = draw_board;

     //Boot
     init_board();
     draw_board();
})(jQuery);