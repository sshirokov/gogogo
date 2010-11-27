(function($) {
     var info = window._info = {
         game: false,
         latest: null,
         player: false,
         color: false,

         interval: false,
         ping: null,

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

     function my_turn(is_it) {
         console.log("Is it my turn?", is_it);
         $('.my-turn').toggle(is_it);
         $('.not.my-turn').toggle(!is_it);
     }

     function register_form(e) {
         var form_data = {},
         url = $(this).attr('action').replace('{game}', info.game);
         $($(this).serializeArray()).each(function(i, v) {
                                              form_data[v.name] = v.value;
                                          });
         $.ajax({url: url,
                 type: $(this).attr('method'),
                 data: JSON.stringify(form_data),

                 success: function(data, text_status, xhr) {
                     console.log("Registered:", data, text_status, xhr);
                     info.player = data.player;
                     info.color = form_data.player;
                     load_my_board();
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

     function skip_move(game, player, callback) {
         callback = callback || function(err, data) {};
         console.log("Want skip:", game, player);

         var url = '/game/' + info.game + '/player/' + info.player + '/skip/';

         $.ajax({url: url,
                 type: "POST",

                 success: function(data, text_status, xhr) {
                     console.log("Skipped:", xhr.status, data, text_status, xhr);
                     load_my_board();
                 },
                 error: function(xhr, text_status, errorThrown) {
                     console.log("Failed to skip:", xhr.status, xhr, text_status, errorThrown);
                 }
                });

         return false;
     }

     function boot_other(callback) {
         callback = callback || function(err, data) { };
         console.log("Booting others: ", info.game, info.player);

         var url = $("#boot-other").attr("action").replace("{game}", info.game).replace("{player}", info.player);

         $.ajax({url: url,
                 type: "POST",
                 success: function(data, text_status, xhr) {
                     console.log("Booted others:", xhr.status, data, text_status, xhr);
                     load_my_board();
                 },
                 error: function(xhr, text_status, errorThrown) {
               console.log("Failed to boot others:", xhr.status, xhr, text_status, errorThrown);
             }
            });

     return false;
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

     function ping(control) {
         if(control !== undefined) {
             if(control) {
                 //Start the pinger
                 ping(false); //Sanity kill
                 info.interval = setInterval(function() { ping(); }, 3000);
             }
             else{
                 //Stop the pinger
                 if(info.interval) clearInterval(info.interval);
                 info.interval = null;
             }
             return;
         }

         var url = "/game/" + info.game + "/";
         if(info.player) url += "player/" + info.player + '/';
         url += "ping/";

         if(info.player) {
             $("#register").hide();
             $("#play").show();
         }
         if(!info.ping) {
             info.ping = $.ajax({url : url,
                                 type: 'POST',

                                 complete: function(xhr, text_status) {
                                     info.ping = null;
                                 },

                                 success: function(data, text_status, xhr) {
                                     if(info.signature && data.gamesig != info.signature) {
                                         console.log("Game out of date!");
                                         load_my_board();
                                     }
                                 },
                                 error: function(xhr, text_status, erroThrown) {
                                     if(info.player && xhr.status == 404) {
                                         info.player = false;
                                         $("#play").hide();
                                         $("#register").show();
                                     }
                                 }
                         });
         }
     }

     function boot() {
         //Register events relevant to a board
         $('#register-form').submit(register_form);
         $("#skip-form").submit(function() { return skip_move(info.game, info.player) });
         $("#boot-other").submit(function() { return boot_other() });

         $("#game.screen .controls").hide();
         $("#game.screen .controls.default").show();
     }

     function load_board(url) {
         console.log("Loading board from:", url);
         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     console.log("We win a board:", data, text_status, xhr, xhr.getResponseHeader('location'));
                     info.latest = data;
                   info.game = data.name;
                   info.state = data.state;

                     if(info.color && !data.over && (data.turn == info.color))
                         my_turn(true);
                     else
                       my_turn(false);

                   console.log("State: ", info.state);

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
             ping(true);
             if(info.latest.over) {
                 $(".messages #player").html("Game Over");
                 $('.endgame').show();
                 $('.endgame #scores').html(JSON.stringify(info.latest.scores));
             }
             else {
                 $(".messages #player").html(info.latest.turn);
                 $('.endgame').hide();
             }

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