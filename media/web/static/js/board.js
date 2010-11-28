(function($) {
     var info = window._info = {
         game: false,
         latest: null,
         player: false,
         color: false,

         branches: {
             current: null,
             all: []
         },

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
         corner_offset: 30,
         stone: 10,

         utils: {
             player_to_color: function(player) {
                 return {'Black': '#000', 'White': '#fff'}[player] || "Salmon";
             },

             x_to_paper: function(x) {
                 return gfx.corner_offset + (
                     x * gfx.utils.step()
                 );
             },

             y_to_paper: function(y) {
                 return gfx.corner_offset + (
                     ((gfx.rows - 1) - y) * gfx.utils.step()
                 );
             },

             step: function() { return (gfx.width - (gfx.corner_offset * 2)) / (gfx.rows - 1); },

             center: function(o) {
                 var bbox = o.getBBox(),
                     dx = (gfx.width / 2) - bbox.x - (bbox.width / 2),
                     dy = (gfx.height / 2) - bbox.y - (bbox.height / 2);
                 console.log("Centering:", o, "bounded", bbox, 'T(' + dx + ',', dy + ')');
                 return o.translate(dx, dy);
             },

             draw: {
                 stone: function(x, y, color) {
                     color = color || "Salmon";
                     return gfx.paper.circle(gfx.utils.x_to_paper(x),
                                             gfx.utils.y_to_paper(y),
                                             gfx.stone).
                                      attr({fill: color});
                 },

                 text: function(x, y, message, options) {
                     function pop_key(o, k, def) { var val = o[k] || def; delete o[k]; return val; }
                     options = $.extend({
                                            size: 15,
                                            font: 'Coolvetica'
                                        }, options || {});
                     return gfx.paper.print(x, y, message,
                                            gfx.paper.getFont(pop_key(options, 'font')),
                                            pop_key(options, 'size')).
                                      attr(options);
                 },

                 highlight: function(x, y, options) {
                     (function(highlight) {
                          //Animate the object we create below
                          highlight.animate({'25%': {'scale': -0.3 },
                                             '50%': {'scale': 1 },
                                             '75%': {'scale': 0.7 },
                                             '100%': {'scale': 0,
                                                      'callback': function() {
                                                          if(arguments.callee.finished) return;
                                                          arguments.callee.finished = true;
                                                          highlight.remove();
                                                      }}
                                            }, 1000);
                      })([0, 0.3, 0.6, 1, 1.5, 2].reduce(
                             //Create a set full of objects to animate
                             function(hl, scale) {
                                 return hl.push(gfx.paper.circle(gfx.utils.x_to_paper(x),
                                                                 gfx.utils.y_to_paper(y),
                                                                 gfx.stone * scale)
                                               ) && hl;
                             },
                             gfx.paper.set()).
                                       attr($.extend({
                                                         'stroke': '#000'
                                                     }, options || {})));
                 },

                 flash: function(message, options) {
                     if(!message) return;
                     (function(flash) {
                          var scale = flash[0].attr('scale');
                          function scale_str(x, y) { return x + " " + y; }
                          flash.animate({'0%': {scale: scale_str(scale.x, scale.y)},
                                         '0%': {opacity: 0, easing: '>'},

                                         '25%': {scale: scale_str(scale.x * 1.3, scale.y * 1.3)},

                                         '50%': {scale: scale_str(scale.x, scale.y), opacity: 1},

                                         '75%': {scale: scale_str(scale.x * 1.3, scale.y * 1.3)},

                                         '100%': {scale: 0, opacity: 0,
                                                  callback: function() {
                                                      if(arguments.callee.finished) return;
                                                      arguments.callee.finished = true;
                                                      flash.remove();
                                                  }}
                                         }, 2000);
                      })(gfx.utils.center(
                             gfx.utils.draw.text(0, 0, message,
                                                 $.extend({
                                                              size: 45,
                                                              fill: 'black',
                                                              stroke: '#ababab',
                                                              'stroke-width': 2
                                                          },
                                                          options,
                                                          {opacity: 0} //Mandatory for animation
                                                 ))));
                 }

             }
         },

         elements: {

         }
     };

     function show_last_move() {
         console.log("Want the last move from:", info.latest.data);
         var move = info.latest.data.moves.slice(-1).pop();

         if(!move) gfx.utils.draw.flash("No moves yet!", {fill: 'red'});
         else if(move.passing) gfx.utils.draw.flash(move.player + " passed", {fill: gfx.utils.player_to_color(move.player)});
         else gfx.utils.draw.highlight(move.x, move.y, {'stroke': gfx.utils.player_to_color(move.player)});
     }

     function load_my_board() {
         gogogo.load_board('/game/' + info.game + '/');
     }

     function create_branch() {try{
         if(!info.player) return false;
         var url = $(this).attr('action').replace('{game}', info.game);
         var form_data = {
             name: $(this).find('input[name=name]:first').val(),
             back: parseInt($(this).find('input[name=back]:first').val()),
             player: info.player
         };

    $(this).find('input[type=text]').val('');

         console.log("Want to create branch:", url, form_data);
         $.ajax({ url: url,
                  type: 'POST',
                  data: JSON.stringify(form_data),

                  success: function(data, text_status, xhr) {
                      console.log("Branch crated:", data, text_status, xhr);
                      load_branches();
                  },
                  error: function(xhr, text_status, errorThrown) {
                      console.log("Couldn't create branch: ", xhr.status, xhr, text_status, errorThrown);
                  }
         });
} catch (x) {
    console.log("Error", x);
}


         return false;
     }

     function change_branch(branch) {
         if(!info.player) return false;
         var url = "/game/{game}/branch/change/".replace("{game}", info.game);

         $.ajax({ url: url,
                  type: 'POST',
                  data: JSON.stringify({ name: branch, player: info.player}),
                  success: function(data, text_status, xhr) {
                      console.log("Branch switched to:", branch, data, text_status, xhr);
                      load_branches();
                  },
                  error: function(xhr, text_status, errorThrown) {
                      console.log("Couldn't switch to branch: ", branch, xhr, text_status, errorThrown);
                  }
                });

         return false;
     }

     function update_branches() {
         $('#branches .current').html(info.branches.current);
         $('#branches .branch').filter(':not(.template)').remove();
         $(info.branches.all).each(function(i, branch) {
                                       var template = $('#branches .branch.template:first').clone();
                                       template.removeClass('template');
                                       template.attr('id',
                                                     template.attr('id').replace('{branch}', branch));
                                       template.html(template.html().replace(/\{branch\}/gm, branch));
                                       $("button", template).click(function() {
                                                                         return change_branch(branch);
                                                                     });
                                       $('#branches .branch.template:first').parent().
                                           append(template);
                                   });
     }

     function load_branches() {
         var url = '/game/' + info.game + '/branch/';
         console.log("Getting branches from:", url);

         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     console.log("Got branches:", data, text_status, xhr);
                     info.branches.current = data.current;
                     info.branches.all = data.branches;

                     update_branches();
                 },
                 error: function(xhr, text_status, errorThrown) {
                     console.log("Failed to get branches:", xhr, text_status, errorThrown);
                 }
                });
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
             $('.controls').show();
             $('.controls.default').hide();
         }
         else {
             info.color = null;
         }
         if(!info.ping) {
             info.ping = $.ajax({url : url,
                                 type: 'POST',

                                 complete: function(xhr, text_status) {
                                     info.ping = null;
                                 },

                                 success: function(data, text_status, xhr) {
                                     info.state = data.state;
                                     if(data.gamesig != info.signature) {
                                         console.log("Game out of date!");
                                         load_branches();
                                         load_my_board();
                                     }
                                 },
                                 error: function(xhr, text_status, erroThrown) {
                                     if(info.player && xhr.status == 404) {
                                         info.player = false;
                                         $('.controls').hide();
                                         $('.controls.default').show();
                                     }
                                 }
                         });
         }

         if(info.state == "Full") {
             $('#register').hide();
         }
         else {
             if(!info.player) $('#register').show();
         }
     }

     function boot() {
         //Register events relevant to a board
         $('#register-form').submit(register_form);
         $("#skip-form").submit(function() { return skip_move(info.game, info.player) });
         $("#boot-other").submit(function() { return boot_other() });
         $('#create-branch-form').submit(create_branch);
         $('#last-move-button').click(show_last_move);

         $("#game.screen .controls").hide();
         $("#game.screen .controls.default").show();
     }

     function load_board(url) {
         if(!info.signature) {
             console.log("We're unsigned. Booting the pinger");
             ping(true);
         }

         console.log("Loading board from:", url);
         $.ajax({url: url,
                 type: 'GET',

                 success: function(data, text_status, xhr) {
                     console.log("We win a board:", data, text_status, xhr, xhr.getResponseHeader('location'));
                     info.latest = data;
                     if(info.game != data.name) {
                         info.game = data.name;
                         load_branches();
                     }
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

         for(var col = 0; col < gfx.cols; col++) {
             var ex, ey,
                 sx = gfx.corner_offset,
                 sy = gfx.corner_offset,
                 distance = gfx.width - (sx * 2),
             ey = distance + sx;
             sx += (gfx.utils.step() * col);
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
             sy += (gfx.utils.step() * row);
             ey = sy;
             var path = "M" + sx + " " + sy + "L" + ex + " " + ey;
             gfx.elements.lines.push(gfx.paper.path(path));
         }

         //Mark the positions on the board
         for(var row = 0; row < gfx.rows; row++) {
             for(var col = 0; col < gfx.cols; col++) {
                 var pos = gfx.paper.circle(gfx.utils.x_to_paper(col),
                                            gfx.utils.y_to_paper(row),
                                            gfx.stone).
                                     attr({fill: '#0f0', 'stroke-opacity': 0, 'fill-opacity': 0});
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

             $(board.positions).each(function(i, v) {
                                         gfx.elements.stones[v.owner] = gfx.elements.stones[v.owner] || [];
                                         gfx.elements.stones[v.owner].push(
                                             gfx.utils.draw.stone(v.x, v.y, gfx.utils.player_to_color(v.owner))
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