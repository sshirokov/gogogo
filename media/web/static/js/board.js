(function($) {
     var info = window._info = {
         game: false,
         latest: null,
         player: false,

         interval: false,
         signature: false
     };
     var gfx = window._gfx = {
         paper: undefined,
         container: '#game',
         width: 500,
         height: 500,
         rows: 19,
         cols: 19,
         step: false,
         corner_offset: 30,
         stone: 10,

         elements: {

         }
     };
     function load_my_board() {
         gogogo.load_board('/game/' + info.game + '/');
     }
     function make_move(game, player, x, y, callback) {
         callback = callback || function(err, data) {};
         console.log("Want move:", game, player, x, y);

         var url = '/game/' + info.game + '/player/' + info.player + '/move/';

         $.ajax({url: url,
                 type: "POST",
                 data: JSON.stringify({x: x, y: y}),

                 success: function(data, text_status, xhr) {
                     console.log("Moved:", xhr.status, data, text_status, xhr);
                     load_my_board();
                 },
                 error: function(xhr, text_status, errorThrown) {
                     console.log("Failed to move:", xhr.status, xhr, text_status, errorThrown);
                 }
         });
     }

     function ping_player() {
       var url = "/game/" + info.game + "/player/" + info.player + "/ping/";
       $("#register").hide();

         info.interval = setInterval(function() {
                                         $.ajax({url : url,
                                                 type: 'POST',

                                                 success: function(data, text_status, xhr) {
                                                     if(info.signature && data.gamesig != info.signature) {
                                                         console.log("Game out of date!");
                                                         gogogo.load_board('/game/' + info.game + '/');
                                                     }
                                                 },
                                                 error: function(xhr, text_status, erroThrown) {
                                                     if(xhr.status == 404) {
                                                         clearInterval(info.interval);
                                                         info.interval = false;
                                                         $("#register").show();
                                                     }
                                                 }
                                               });
                                     },
                                     3000);
     }

     function boot() {
         //Register events relevant to a board
         function register_form(e) {
             var data = {},
                 url = $(this).attr('action').replace('{game}', info.game);
             $($(this).serializeArray()).each(function(i, v) {
                                                  data[v.name] = v.value;
                                              });
             $.ajax({url: url,
                     type: $(this).attr('method'),
                     data: JSON.stringify(data),

                     success: function(data, text_status, xhr) {
                         console.log("Registered:", data, text_status, xhr);
                         info.player = data.player;
                         ping_player();
                     },
                     error: function(xhr, text_status, errorThrown) {
                         console.log("Failed:", xhr, text_status, errorThrown);
                         if(xhr.status == 409) {
                             console.log("Already have a player registration");
                         }
                     }
             });
             return false;
         }
         $('#register-form').submit(register_form);
     }

     function load_board(url) {
         console.log("Loading board from:", url);
         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     console.log("We win a board:", data, text_status, xhr, xhr.getResponseHeader('location'));
                     info.latest = data;
                     info.game = data.name;
                     if(data.over) {
                         $(".messages #player").html("Game Over");
                     }
                     else {
                         $(".messages #player").html(data.turn);
                     }

                     window.gogogo.draw_board(data.data, data.gamesig);

                     return false;
                 },

                 error: function(xhr, text_status, errorThrown) {
                     console.log("We lose:", xhr, text_status, errorThrown);

                     return false;
                 }
         });
     }

     function draw_board(board, signature) {
         gfx.paper.clear();
         gfx.elements = {};

         //Draw underling board
         gfx.elements.base = gfx.paper.rect(10, 10, 480, 480, 5);
         gfx.elements.base.attr('fill', "#D1D190");
         gfx.elements.lines = [];
         gfx.elements.stones = {};
         gfx.elements.positions = [];
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

         //Mark the positions on the board
         for(var row = 0; row < gfx.rows; row++) {
             for(var col = 0; col < gfx.cols; col++) {
                 var pos = gfx.paper.circle(gfx.corner_offset + (
                                                col * gfx.step
                                            ),
                                            gfx.corner_offset + (
                                                ((gfx.rows - 1) - row) * gfx.step
                                            ),
                                            gfx.stone).attr({fill: '#0f0', 'stroke-opacity': 0, 'fill-opacity': 0});
                 pos.hover(function (event) {
                               this.attr({'fill-opacity': 0.25});
                           }, function (event) {
                               this.attr({'fill-opacity': 0});
                           });
                 var make_click = function(x, y) {
                     return function(even) {
                         console.log("Clicked:", this, x, y);
                         window.gogogo.make_move(info.game, info.player, x, y, function(err, data) {
                                                if(err) console.log("Error:", data);
                                                else console.log("Moved:", data);
                                            });
                     };
                 };
                 pos.click(make_click(col, row));

               gfx.elements.positions.push(pos);
             }
         }

         //Render board if we have one
         if(board && signature) {
             info.signature = signature;
             function player_to_color(player) {
                 return {'Black': '#000', 'White': '#fff'}[player];
             }

             $(board.positions).each(function(i, v) {
                                     console.log("Stored position:", v.owner, "(" + v.x + ",", v.y + ")");
                                         gfx.elements.stones[v.player] = gfx.elements.stones[v.player] || [];
                                         gfx.elements.stones[v.player].push(
                                             gfx.paper.circle(gfx.corner_offset + (
                                                                  v.x * gfx.step
                                                              ),
                                                              gfx.corner_offset + (
                                                                  ((board.height - 1) - v.y) * gfx.step
                                                              ),
                                                              gfx.stone).
                                                       attr({fill: player_to_color(v.owner)})
                                         );
                                 });

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
     window.gogogo.make_move = make_move;

     //Boot
     $(function() {
           boot();
           init_board();
           draw_board();
     });
})(jQuery);