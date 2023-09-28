import asyncio
import websockets
import json
import os

from game import init_game, draw_card, play_card, autoplay_card, game_state_view_as, is_game_over, draw_update_state, play_update_state

# server_host, server_port = 'localhost', 8765 # local
server_host, server_port = '', int(os.environ.get("PORT")) # production


# 存儲房間和玩家的資訊
player_conns = {} # conn_id => (room_id, player_id)
room_conns = {} # room_id => [conn...]
conn2room = {} # conn_id => room_id
# NOTE: if conn_id in player_conns, then conn is gamming
games = {} # room_id => game



# 發送訊息給指定對象
async def notify(conn, json_str):
  print(f'DEBUG: notify conn#{conn.id}', json_str)
  await conn.send(json_str)
  # print(f'DEBUG: _notify to conn#{conn.id} done')


# 發送訊息給群體
async def notify_all(room_id, json_str):
  conns = room_conns[room_id]
  for conn in conns:
    await notify(conn, json_str)


# 通知玩家行動/等待
async def send_turn_notify(room_id):
  print(f'DEBUG: send_turn_notify room#{room_id}')
  game_state = games.get(room_id)
  conns = room_conns[room_id]
  current_player_id = game_state["current_player"]
  other_player_id = 2 if current_player_id == 1 else 1  # 對手
  current_player_conn = conns[current_player_id-1]
  other_player_conn = conns[other_player_id-1]

  json_str1 = json.dumps({"message": "輪到你的回合", "gameEvent": "turnStart"}, ensure_ascii=False)
  await notify(current_player_conn, json_str1)

  json_str2 = json.dumps({"message": "輪到對手的回合", "gameEvent": "waitOther"}, ensure_ascii=False)
  await notify(other_player_conn, json_str2)


# 遊戲開始
async def game_start(room_id):
  print(f'DEBUG: game_start room#{room_id}')

  conns = room_conns[room_id]
  player_conns[conns[0].id] = (room_id, 1)
  player_conns[conns[1].id] = (room_id, 2)
  games[room_id] = init_game()
  
  game_state_view_as1 = game_state_view_as(games[room_id], 1)
  json_str1 = json.dumps({ "message": "game start", "gameEvent": "setState", "gameData": game_state_view_as1}, ensure_ascii=False)
  await notify(conns[0], json_str1)

  game_state_view_as2 = game_state_view_as(games[room_id], 2)
  json_str2 = json.dumps({ "message": "game start", "gameEvent": "setState", "gameData": game_state_view_as2}, ensure_ascii=False)
  await notify(conns[1], json_str2)

  # 個別通知雙方玩家回合行動
  await send_turn_notify(room_id)


# 遊戲結束
async def game_over(room_id):
  print(f'DEBUG: game_over room#{room_id}')
  game_state = games.get(room_id)
  message = f"遊戲結束，贏家是玩家{game_state['winner']}"
  json_str = json.dumps({ "message": message, "gameEvent": "gameOver" }, ensure_ascii=False)
  await notify_all(room_id, json_str)


# 判斷連線是否在遊戲中？
def is_gaming(conn): return conn.id in player_conns
# 取得連線相關的遊戲資訊
def get_room_player_from_conn(conn): return player_conns[conn.id]

# 判斷連線的玩家是否可以行動？
def is_player_active(conn):
  if not is_gaming(conn): return False
  room_id, player_id = get_room_player_from_conn(conn)

  # 確認是否為正確的遊戲房號？
  #if not (room_id in games): return False

  game_state = games[room_id]
  current_player_id = game_state["current_player"]
  return player_id == current_player_id

# 玩家抽牌
async def player_draw_card(room_id):
  game_state = games.get(room_id)
  updated_state = draw_card(game_state)

  conns = room_conns[room_id]
  current_player_id = game_state["current_player"]
  other_player_id = 2 if current_player_id == 1 else 1  # 對手

  # 行動玩家得到狀態更新
  current_player_conn = conns[current_player_id-1]
  game_data = draw_update_state(updated_state, current_player_id)
  json_str1 = json.dumps({"message": "你抽出了一張牌", "gameEvent": "setState", "gameData": game_data }, ensure_ascii=False)
  await notify(current_player_conn, json_str1)

  # 等待玩家得到訊息通知
  other_player_conn = conns[other_player_id-1]
  json_str2 = json.dumps({"message": "對手抽出了一張牌", "gameEvent": "waitOther"}, ensure_ascii=False)
  await notify(other_player_conn, json_str2)

  game_state.update(updated_state) # NOTE: 慣例，一切都結束後才更新


# 玩家出牌
async def player_play_card(room_id):
  game_state = games.get(room_id)
  updated_state = autoplay_card(game_state) # TODO 改成正式的 play_card()

  conns = room_conns[room_id]
  current_player_id = game_state["current_player"]
  other_player_id = 2 if current_player_id == 1 else 1  # 對手
  
  # 行動玩家得到狀態更新 (自身手牌、對手生命)
  game_data1 = play_update_state(updated_state, current_player_id, current_player_id)
  current_player_conn = conns[current_player_id-1]
  # TODO 更加細緻完整的遊戲紀錄 (第一人稱)
  json_str1 = json.dumps({"message": "你造成了傷害", "gameEvent": "setState", "gameData": game_data1 }, ensure_ascii=False)
  await notify(current_player_conn, json_str1)
  
  # 等待玩家得到狀態更新 (自身生命)
  game_data2 = play_update_state(updated_state, current_player_id, other_player_id)
  other_player_conn = conns[other_player_id-1]
  # TODO 更加細緻完整的遊戲紀錄 (第一人稱)
  json_str2 = json.dumps({"message": "對手對你造成了傷害", "gameEvent": "setState", "gameData": game_data2 }, ensure_ascii=False)
  await notify(other_player_conn, json_str2)

  game_state.update(updated_state) # NOTE: 需要一切都結束後才更新，確保 current_player 是當前回合的值

# 回合結束，判定遊戲是否結束？切換行動玩家
async def end_turn(room_id):
  game_state = games.get(room_id)
  if not is_game_over(game_state): # 遊戲還沒結束
    await send_turn_notify(room_id)
  else:
    await game_over(room_id)


# 定義 WebSocket 伺服器的處理邏輯
async def game_server(conn, path):
  print(f'DEBUG: create conn#{conn.id}')
  async for message in conn:
    data = json.loads(message)
    action = data.get("action")
    payload = data.get("payload")
    print('message', conn.id, action, payload)
    if action:
      if action == "create_room": # 創建房間
        print('DEBUG: room_conns', room_conns)
        
        room_id = len(room_conns) + 1
        room_conns[room_id] = [conn]
        conn2room[conn.id] = room_id
        print('create room', room_conns[room_id])

        response = {"message": f"Room created with ID {room_id}"}
        await conn.send(json.dumps(response, ensure_ascii=False))

      elif action == "join_room": # 加入房間
        print('DEBUG: room_conns', room_conns)
        room_id = payload.get("room_id")
        if room_id in room_conns and len(room_conns[room_id]) < 2:
          room_conns[room_id].append(conn)
          conn2room[conn.id] = room_id
          print('join room', room_conns[room_id])

          response = {"message": f"Joined room {room_id}"}
          await conn.send(json.dumps(response, ensure_ascii=False))
        else:
          response = {"error": "Room is full or does not exist"}
          await conn.send(json.dumps(response), ensure_ascii=False)

      elif action == "chat": # 房間聊天
        room_id = conn2room[conn.id]
        message = payload.get("message")
        response = { "message": message }

        await notify_all(room_id, json.dumps(response, ensure_ascii=False))

      elif action == "start_game": # 開始遊戲
        room_id = payload.get("room_id")
        if room_id in room_conns and len(room_conns[room_id]) == 2:
          response = {"message": "Starting the game..."}
          await conn.send(json.dumps(response, ensure_ascii=False))
          # 在這裡可以加入遊戲的邏輯
          await game_start(room_id)
        else:
          response = {"error": "Invalid room or not enough players"}
          await conn.send(json.dumps(response, ensure_ascii=False))

      elif action == "player_draw_card": # 玩家抽牌
        print('player_draw_card')
        if is_player_active(conn):
          room_id, player_id = get_room_player_from_conn(conn)
          await player_draw_card(room_id)
        else:
          response = {"error": "非行動玩家或遊戲房間不存在"}
          await conn.send(json.dumps(response, ensure_ascii=False))

      elif action == "player_play_card": # 玩家出牌
        print('player_play_card')
        if is_player_active(conn):
          room_id, player_id = get_room_player_from_conn(conn)
          await player_play_card(room_id)
          await end_turn(room_id)
        else:
          response = {"error": "非行動玩家或遊戲房間不存在"}
          await conn.send(json.dumps(response, ensure_ascii=False))
  print(f'DEBUG: conn#{conn.id} is disconnected')



# 啟動 WebSocket 伺服器
async def main():
    start_server = await websockets.serve(game_server, server_host, server_port)
    print(f"WebSocket server started on ws://{server_host}:{server_port}")

    await start_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
