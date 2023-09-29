# websocket-game-examle

sample websocket game.

you can play on [this demo](https://outshaker.github.io/websocket-game-examle/room.html)

1. you can create room or join room
2. when room has 2 player, you can start game
3. when in your turn, you can draw card and play card (click button)
4. when one player's HP <= 0, game is over

Warning: this is just a game prototype without any security protection measures. Please do not exchange personal privacy information on it.

## folder: /websockets-quick-start

example from (https://websockets.readthedocs.io/en/stable/howto/quickstart.html)

## demo

backend:
- game.py: game logic
- room.py: server

frontend:
- room.html: client
- style.css
- script.js

1. install websockets module `pip install websockets`
2. launch server `python room.py`
3. open "room.html" in browser

