
# A very simple Flask Hello World app for you to get started with...
import chess
import chess.engine
import chess.polyglot
import datetime
import datetime
import chess.svg
import random
import time
from flask import Flask, request

app = Flask(__name__)
def get_move(board, engine, moves_count, difficulty):
    move = None
    if moves_count <= 6: # book move
        opening_moves = []
        with chess.polyglot.open_reader('/home/jimmyrustles/chess/Perfect2017.bin') as reader:
            for entry in reader.find_all(board):
                if entry.weight >= 100 or len(opening_moves) < 3: opening_moves.append(entry.move)
        if len(opening_moves) == 0:
            move = None
        else:
            move = random.choice(opening_moves)
    if moves_count > 6 or move == None: # non-book move
        node_limit = 30000
        time_limit = 250
        if difficulty <= 15:
            node_limit = 18000
            time_limit = 150
        if difficulty <= 10:
            node_limit = 10000
            time_limit = 30
        if difficulty <= 5:
            node_limit = 5000
            time_limit = 30
        if difficulty <= 2:
            time_limit = 30
            node_limit = 1500
        time_limit /= 1000
        with engine.analysis(board, chess.engine.Limit(time=time_limit, nodes=node_limit)) as analysis:
            for info in analysis:
                pass
        move = analysis.info['pv'][0]
    return move

def sortFunc(score):
    score_val = score.split("|")[7]
    new_score_val = ""
    for letter in score_val:
        if letter >= '0' and letter <= '9':
            new_score_val += letter
    score_val = str(new_score_val)
    score_val = int(score_val)
    return score_val

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    start_time = -1
    leaderboard = False
    game_ended = False
    board = chess.Board()
    outstr = """<html>
    <head><title>Blindfold Chess</title>"""
    outstr += """
    <style>
    table, th, td {
        border: 1px solid;
    }

    table {
        width: 75%;
    }
    </style>
    <script>
    setTimeout(function() {
    window.scroll({
  top: 225,
  left: 0,
  behavior: 'smooth'
});
    }, 75);
    </script>"""
    outstr += """</head>
    <body>
    <center>
    <h2>Blindfold Chess</h2>
    <img src=\"/images/chess_head.jpg\" width=200>
    <br><br>"""
    if request.method == "GET":
        #outstr += "<br>form: " + str(("leaderboard" in request.form)) + "<br>"
        #outstr += "<br>form: " + str(request.args.get("leaderboard")) + "<br>"
        if str(request.args.get("leaderboard")) == "Show Leaderboard":
            outstr += """
            <font color="green">
            <table>
            <tr>
            <td>Rank</td>
            <td>Name</td>
            <td>Date</td>
            <td>Difficulty</td>
            <td>Used hints</td>
            <td>Colour</td>
            <td>Time</td>
            <td>Outcome</td>
            <td>Score</td>
            </tr>"""
            ff = open('/home/jimmyrustles/chess/highscores.txt','r')
            lines = ff.readlines()
            ff.close()
            scores = []
            for line in lines:
                scores.append(line.replace("\n",""))
            scores.sort(key=sortFunc, reverse=True)
            #outstr += "<br>" + str(scores) + "<br>"
            rank = 0
            for score in scores:
                rank += 1
                score_split = score.split("|")
                name = score_split[0]
                date = score_split[1]
                difficulty = score_split[2]
                used_hints = score_split[3]
                colour = score_split[4].capitalize()
                time_seconds = int(float(score_split[5]))
                outcome = score_split[6]
                score_val = score_split[7].replace("\n","")
                new_score_val = ""
                for letter in score_val:
                    if letter >= '0' and letter <= '9':
                        new_score_val += letter
                score_val = str(new_score_val)
                score_val = int(score_val)
                cell_col = "black"
                if outcome == "Computer Wins":
                    cell_col = "red"
                if outcome == "Player Wins":
                    cell_col = "green"

                duration = int(time_seconds)
               # outstr += ":::" + str(duration) + ":::"
                tot_hours = duration / 60 / 60
                tot_mins = duration / 60
                tot_secs = duration
                show_hours = int(tot_hours)
                show_mins = tot_mins - int(show_hours * 60)
                show_mins = int(show_mins)
                # 4000 -
                show_secs = tot_secs - int(int(show_mins) * 60) - int(int(show_hours) * 60 * 60)
                show_secs = int(show_secs)
                show_hours_str = str(show_hours)
                show_mins_str = str(show_mins)
                show_secs_str = str(show_secs)
                if len(show_hours_str) < 2: show_hours_str = "0" + show_hours_str
                if len(show_mins_str) < 2: show_mins_str = "0" + show_mins_str
                if len(show_secs_str) < 2: show_secs_str = "0" + show_secs_str
                time_string = show_hours_str + ":" + show_mins_str + ":" + show_secs_str
                outstr += "<tr><td><font color=\"" + cell_col + "\">" + str(rank) + "</td><td><font color=\"" + cell_col + "\">" +  name + "</td><td><font color=\"" + cell_col + "\">" + date + "</td><td><font color=\"" + cell_col + "\">" + difficulty + "</td><td><font color=\"" + cell_col + "\">" + used_hints + "</td><td><font color=\"" + cell_col + "\">" + colour + "</td><td><font color=\"" + cell_col + "\">" + str(time_string) + "</td><td><font color=\"" + cell_col + "\">" + outcome + "</td><td><font color=\"" + cell_col + "\">" + str(format(score_val,",")) + "</td></tr>"
            outstr += """
            </table>
            <font color="black">"""
            outstr += "<a href=\"/\">Start new game</a>"
            leaderboard = True
            pass
    if request.method == "POST":
        engine_file = "/home/jimmyrustles/chess/stockfish_10_x64"
        try:
            engine = chess.engine.SimpleEngine.popen_uci(engine_file)
        except:
            outstr += "Unable to load engine. Try refreshing in a few seconds."
            return outstr
        difficulty = 1
        hint_mode = "Show None"
        hint_set = False
        if 'difficulty' in request.form:
            difficulty = int(request.form['difficulty'])
        if 'hint' in request.form:
            hint_set = True
            hint_mode = request.form['hint']
        elif 'hint_mode' in request.form:
            hint_set = True
            hint_mode = request.form['hint_mode']

        hints_used = False
        if 'hints_used' in request.form:
            if request.form['hints_used'] == 'True':
                hints_used = True

        if 'leaderboard' in request.form:
            outstr += "<br><br>Showing leaderboard<br><br>"
        if 'high_score_name' not in request.form:
            outstr += "<br>Difficulty: " + str(difficulty) + "<br><br>"
        engine.configure({"Skill Level": difficulty})
        colour = request.form['colour']
        if colour == "random":
            colour = "white"
            if random.randint(0,1) == 1:
                colour = "black"
        moves = request.form['game_moves']
        if 'start_time' in request.form:
            start_time = int(float(request.form['start_time']))
        orig_moves = str(moves)
        moves_count = moves.count(' ')
        past_string = ""
        in_move = ""
        if "input_move_orig" in request.form:
            in_move = request.form['input_move_orig']
        if "input_move" in request.form:
            in_move = request.form['input_move']
        in_move = in_move.strip()
        if "past_string" in request.form:
            if len(request.form['past_string']) > 0 and in_move == "":
                outstr += request.form['past_string']
                outstr += "<br>" + str(in_move) + "<br>"
        if moves == "startpos" and in_move == "":
            if colour == "white":
                outstr += "<b>Starting Position</b>"
                outstr += "<br>"
            else:
                move = get_move(board, engine, moves_count, difficulty)
                move_san = board.san(move)
                board.push_san(move_san)
                outstr += "Computer plays: <b>" + str(move_san) + "</b><br>"
                past_string += "Computer plays: <b>" + str(move_san) + "</b><br>"
                moves = "startpos " + str(move_san)
                pass
            if start_time == -1:
                start_time = time.time()
        elif moves_count == 2:
            if start_time == -1:
                start_time = time.time()
        else:
            pass
        #input_move = request.form['input_move']
        if orig_moves != "startpos":
            # play through all moves
            full_moves = moves.replace("startpos ", "")
            for move in full_moves.split(" "):
                try:
                    board.push_san(move)
                except:
                    outstr += "<br>Error: Unable to play past moves.<br>"
                    outstr += "<br>failed on: " + str(move) + "<BR>"
        if len(in_move) > 0:
             # player has entered a move
            if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition() or board.is_checkmate():
                game_ended = True
            if not game_ended:
                worked = False
                try:
                    board.push_san(in_move)
                    worked = True
                except:
                    outstr += in_move + " is an invalid move.<br>"
                    worked = False
                if worked:
                    #outstr += "<br>Played " + in_move + "<br>"
                    #past_string += "<br>Played " + in_move + "<br>"
                    moves += " " + in_move
                    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition() or board.is_checkmate():
                        game_ended = True
                if not game_ended and worked:
                    move = get_move(board, engine, moves_count, difficulty)
                    move_san = board.san(move)
                    board.push_san(move_san)
                    outstr += "Computer plays: <b>" + str(move_san) + "</b><br>"
                    past_string += "Computer plays: <b>" + str(move_san) + "</b><br>"
                    moves += " " + move_san
        engine.quit()
        player_wins = False
        draw = False
        computer_wins = False
        if board.is_stalemate():
            if 'high_score_name' not in request.form:
                outstr += "<br>Game drawn by stalemate.<br>"
            game_ended = True
            draw = True
        if board.is_insufficient_material():
            if 'high_score_name' not in request.form:
                outstr += "<br>Game drawn by insufficient material.<br>"
            game_ended = True
            draw = True
        if board.can_claim_fifty_moves():
            if 'high_score_name' not in request.form:
                outstr += "<br>Game drawn by 50-move rule.<br>"
            game_ended = True
            draw = True
        if board.can_claim_threefold_repetition():
            if 'high_score_name' not in request.form:
                outstr += "<br>Game drawn by threefold repetition.<br>"
            game_ended = True
            draw = True
        outcome = "Draw"
        if board.is_checkmate():
            turn_col = "white"
            if board.turn:
                # white got checkmated
                if colour == "white":
                    computer_wins = True
                    outcome = "Computer Wins"
                elif colour == "black":
                    player_wins = True
                    outcome = "Player Wins"
            elif not board.turn:
                # black got checkmated
                if colour == "black":
                    computer_wins = True
                    outcome = "Computer Wins"
                elif colour == "white":
                    player_wins = True
                    outcome = "Player Wins"
            if 'high_score_name' not in request.form:
                outstr += "<BR>" + turn_col.capitalize() + " wins by checkmate.<BR>"
            game_ended = True
        stop_output = False
        if game_ended:
            time_seconds = 0
            if 'high_score_name' not in request.form:
                if player_wins: outstr += "<BR>Congratulations! You won!<BR><br>"
                else: outstr += "<br><br>"
                outstr += "Difficulty: " + str(difficulty) + "<br>"
                duration = time.time() - int(start_time)
                duration = int(duration)
                tot_hours = duration / 60 / 60
                tot_mins = duration / 60
                tot_secs = duration
                show_hours = int(tot_hours)
                show_mins = tot_mins - int(show_hours * 60 * 60)
                show_mins = int(show_mins)
                show_secs = tot_secs - int(show_mins * 60)
                show_secs = int(show_secs)
                show_hours_str = str(show_hours)
                show_mins_str = str(show_mins)
                show_secs_str = str(show_secs)
                if len(show_hours_str) < 2: show_hours_str = "0" + show_hours_str
                if len(show_mins_str) < 2: show_mins_str = "0" + show_mins_str
                if len(show_secs_str) < 2: show_secs_str = "0" + show_secs_str
                time_string = show_hours_str + ":" + show_mins_str + ":" + show_secs_str
                outstr += "<br>Your time: " + time_string + "s<br>"
                #outstr += """Your time: 00:00:00<br>
                #Used hints: """
                outstr += "Used hints: " + str(hints_used) + "<br>"
                outstr += "Colour: " + colour.capitalize() + "<br><br>"
            score = 0
            if player_wins:
                score += 10000000
            if draw:
                score += 5000000
            if computer_wins:
                pass
            if colour == "black":
                score += 50
            if not hints_used:
                score += 1000000000
            score += difficulty * 100000
            time_seconds = time.time() - int(float(request.form['start_time']))
            time_seconds = int(time_seconds)
            seconds_score = 3600 - time_seconds
            if seconds_score < 0: seconds_score = 0
            if seconds_score > 3600: seconds_score = 3600
            score += seconds_score
            if 'high_score_name' not in request.form:
                outstr += "Final board: <br>"
                boardsvg = chess.svg.board(board, orientation=board.turn, size=400)
                outstr += "" + str(boardsvg) + "<BR>"
                new_moves = moves.replace("startpos ", "")
                new_move_string = ""
                i = -1
                for move in new_moves.split(" "):
                    i += 1
                    if i % 2 == 0:
                        new_move_string += str(int((i+2) / 2)) + ". "
                    new_move_string += move + " "
                duration = time.time() - int(start_time)
                outstr += "Game moves: " + new_move_string + "<BR><BR>"
                outstr += "Your score: <b>" + "{:,}".format(score) + "</b><br><br>"
                outstr += "<form method=\"post\"><input type=\"hidden\" name=\"game_moves\" value=\"" + moves + "\">"
                outstr += "<input type=\"hidden\" name=\"difficulty\" value=\"" + str(difficulty) + "\">"
                if 'input_move' in request.form:
                    outstr += "<input type=\"hidden\" name=\"input_move_orig\" value=\"" + request.form['input_move'] + "\">"
                outstr += "<input type=\"hidden\" name=\"colour\" value=\"" + colour + "\">"
                outstr += "<input type=\"hidden\" name=\"score\" value=\"" + str(score) + "\">"
                outstr += "<input type=\"hidden\" name=\"hints_used\" value=\"" + str(hints_used) + "\">"
                outstr += "<input type=\"hidden\" name=\"outcome\" value=\"" + str(outcome) + "\">"
                outstr += "<input type=\"hidden\" name=\"time_seconds\" value=\"" + str(duration) + "\">"
                outstr += "<input type=\"hidden\" name=\"start_time\" value=\"" + str(start_time) + "\">"
                outstr += "Submit your high score:<br>"
                outstr += "(High scores with malicious or spoofed values will be removed)<br>"
                outstr += "Name: <input type=\"text\" name=\"high_score_name\" value=\"\"> <input type=\"submit\" name=\"submit_high_score\"><br><br>"
                outstr += "</form>"
            stop_output = True
            if 'high_score_name' in request.form:
                ff = open('/home/jimmyrustles/chess/highscores.txt', 'r', encoding="utf-8")
                lines = ff.readlines()
                lastline = ""
                if len(lines) > 0:
                    lastline = lines[len(lines) - 1]
                    line_split = lastline.split("|")
                    time_seconds_read = int(float(line_split[5]))
                    name_read = line_split[0]
                ff.close()
                ff = open('/home/jimmyrustles/chess/highscores.txt', 'a', encoding="utf-8")
                current_date = str(datetime.datetime.today()).split()[0]
                time_seconds = time.time() - int(float(request.form['start_time']))
                time_seconds = int(float(request.form['time_seconds']))
                allow_write = True
                if time_seconds == time_seconds_read and name_read == request.form['high_score_name'].replace("|",""):
                    allow_write = False
                if allow_write:
                    writestr = request.form['high_score_name'].replace("|","").replace("<","-").replace(">","-").replace("&","-") + "|" + current_date + "|" + str(difficulty) + "|" + str(hints_used) + "|" + colour + "|" + str(time_seconds) + "|" + outcome + "|" + str(score)
                    ff.write(writestr + "\n")
                    ff.close()
                    outstr += "High score submitted!<br><br> Name: " + request.form['high_score_name'] + "<br>"
                    outstr += "Score: " + str(score) + "<br><br>"
                else:
                    outstr += "Duplicate write detected, high score submission cancelled.<br><br>"
            stop_output = True
        if 'hint' in request.form or 'hint_mode' in request.form and not stop_output:
            if not hint_set: hint_mode = request.form['hint']
            if hint_mode == 'Show Board' or hint_mode == 'Show Board + Moves':
                boardsvg = chess.svg.board(board, orientation=board.turn, size=400)
                outstr += "" + str(boardsvg) + "<BR>"
                hints_used = True
            if hint_mode == 'Show Empty Board' or hint_mode == "Show Empty Board + Moves":
                emptyboard = chess.Board("8/8/8/8/8/8/8/8 w - - 0 1")
                boardsvg = chess.svg.board(emptyboard, orientation=board.turn, size=400)
                outstr += "" + str(boardsvg) + "<BR>"
                hints_used = True
        outstr += "<form method=\"post\"><input type=\"hidden\" name=\"game_moves\" value=\"" + moves + "\">"
        outstr += "<input type=\"hidden\" name=\"difficulty\" value=\"" + str(difficulty) + "\">"
        outstr += "<input type=\"hidden\" name=\"start_time\" value=\"" + str(start_time) + "\">"
        if 'input_move' in request.form:
            outstr += "<input type=\"hidden\" name=\"input_move_orig\" value=\"" + request.form['input_move'] + "\">"
        outstr += "<input type=\"hidden\" name=\"colour\" value=\"" + colour + "\">"
        if 'hint' in request.form or 'hint_mode' in request.form and not stop_output:
            if hint_mode == 'Show Moves' or hint_mode == 'Show Board + Moves' or hint_mode == "Show Empty Board + Moves":
                new_moves = moves.replace("startpos ", "")
                new_move_string = ""
                i = -1
                for move in new_moves.split(" "):
                    i += 1
                    if i % 2 == 0:
                        new_move_string += str(int((i+2) / 2)) + ". "
                    new_move_string += move + " "
                outstr += "Game moves: " + new_move_string + "<BR>"
                hints_used = True
        if not stop_output:
            if past_string == "" and 'past_string' in request.form: past_string = request.form['past_string']
            outstr += "<input type=\"hidden\" name=\"past_string\" value=\"" + past_string + "\">"
            outstr += "<input type=\"hidden\" name=\"hints_used\" value=\"" + str(hints_used) + "\">"

            outstr += "<input type=\"hidden\" name=\"hint_mode\" value=\"" + hint_mode + "\">"
            outstr += "<input type=\"hidden\" name=\"start_time\" value=\"" + str(start_time) + "\">"
            if not game_ended:
                outstr += """Enter move: <input type="text" name="input_move" value="" autofocus> <input type="submit" action="move" hint=\""""
                outstr += hint_mode
                outstr += """\" id='makemove' value="Make Move"><br>"""
            outstr += "Hints: <input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show Board\"> "
            outstr += "<input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show Moves\"> "
            outstr += "<input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show Board + Moves\"> <br>"
            outstr += "<input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show Empty Board\"> "
            outstr += "<input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show Empty Board + Moves\"> "
            outstr += "<input type=\"submit\" action=\"move\" name=\"hint\" value=\"Show None\"><br><br>"
            outstr += "</form><br><br>"
        outstr += "<a href=\"/\">Start new game</a>"
        pass
    elif not leaderboard:
        # new game screen

        outstr += """
        <h1>New Game</h1>
        <form method="post">
        <input type="hidden" name="startgame" value="start">
        <input type="hidden" name="game_moves" value="startpos">
        Play as: <input type="radio" name="colour" value="white" id="white">
        <label for="white">White</label>
        <input type="radio" name="colour" value="black" id="black">
        <label for="black">Black</label>
        <input type="radio" name="colour" value="random" id="random" checked>
        <label for="random">Random</label>
        <br><br>
        Difficulty: <input type="range" name="difficulty" value="1" min="1" max="20" oninput="this.nextElementSibling.value = this.value">
        <output>1</output>
        <br><br>
        <input type="submit" action="startgame" value="Start Game"></form>
        <br><br>"""
    if leaderboard or game_ended or 'colour' not in request.form:
        outstr += "</form><form method=\"GET\"><br><br><input type=\"submit\" name=\"leaderboard\" value=\"Show Leaderboard\"><br><br>"
    outstr += "</form>"
    outstr += """<br><br>Comments, suggestions, feedback<br>
    sgriffin53@gmail.com<br><br>"""
    outstr += """Donate<br>
    If you'd like to donate to the author, donations are accepted via crypto and paypal<br>
    BTC: 31h7erNaay3NeAtMRp7z817xHX2ZyPNKkL<BR>
    ETH: 0xb582E7C92abE668C7fDc36c9319cB50845CEB70E<BR>
    DOGE: DG4C6GSsQxu2hnA2NfCJZWxH9E9sAvV3Lq<BR>
    LTC: MAxRiUGjYwMMyqqXyQX8m1psqPWvoJWhzn<BR>
    Paypal: sgriffin53@gmail.com<br>"""
    outstr += """<BR><BR>
    Attribution<br>
    Stockfish 10 64-bit linux version is used for all engine calculations. <a href=\"https://stockfishchess.org\">stockfishchess.org</a><br>
    \"Head for Chess 62:365\" by andreasnilsson1976 is licensed under CC BY-NC-ND 2.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-nd/2.0/?ref=openverse.
    </body></html>"""
    return outstr

