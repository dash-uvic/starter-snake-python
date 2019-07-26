#!/bin/bash

NAME="battlesnake"

tmux kill-session -t $NAME &> /dev/null

#This will create four windows:
# Top:0.0    - the game engine
# Left:0.1   - snake 1 on port 8080
# Right:0.2  - snake 2 on port 8081
# Bottom:0.3 - run the game 
tmux new-session -s $NAME -n $NAME -d
tmux split-window -t $NAME -p 80 
tmux split-window -d 
tmux split-window -h


#Start the game engine
tmux send-keys -t $NAME:0.0 'cd bin/ && ./engine dev' C-m
sleep 1

#Activate the virtenv 
tmux send-keys -t $NAME:0.1 'source venv/bin/activate' C-m
tmux send-keys -t $NAME:0.2 'source venv/bin/activate' C-m
tmux send-keys -t $NAME:0.3 'source venv/bin/activate' C-m

#Start the snake on different ports and colors 
tmux send-keys -t $NAME:0.1 'python app/main.py -c "#ff00ff" -p 8080' C-m
tmux send-keys -t $NAME:0.2 'python app/main.py -c "#0000ff" -p 8081' C-m

#Run a game and run 1 game
tmux send-keys -t $NAME:0.3 'python run_game.py -n 1' C-m

tmux attach -t $NAME

