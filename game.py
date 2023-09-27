import random

def init_game():
  # 初始玩家生命值
  initial_health = 15

  # 初始卡牌堆
  player1_deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  player2_deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  player1_hand = [player1_deck.pop(random.randint(0, len(player1_deck) - 1))]
  player2_hand = [player2_deck.pop(random.randint(0, len(player2_deck) - 1))]

  # 遊戲狀態字典
  game_state = {
    "player1_health": initial_health,
    "player2_health": initial_health,
    "player1_deck": player1_deck,
    "player2_deck": player2_deck,
    "player1_hand": player1_hand,
    "player2_hand": player2_hand,
    "current_player": 1,  # 1代表玩家1，2代表玩家2
    "winner": None  # 初始沒有獲勝者
  }
  return game_state

def draw_card(game_state):
  current_player = game_state["current_player"]
  deck = game_state[f"player{current_player}_deck"]
  hand = game_state[f"player{current_player}_hand"]

  if len(deck) > 0:
    # 從卡牌堆中隨機抽一張卡牌
    card_index = random.randint(0, len(deck) - 1)
    card_id = deck.pop(card_index)
    # 把卡牌加入手牌
    hand.append(card_id)
    print(f'玩家{current_player} 抽出 {card_id} 並加入手牌')

  # 更新遊戲狀態
  updated_state = {
    f"player{current_player}_deck": deck,
    f"player{current_player}_hand": hand,
  }
  return updated_state

# TODO 事前排除 card_id 不在玩家手牌中的案例
def play_card(game_state, card_id):
  current_player = game_state["current_player"]
  other_player = 2 if current_player == 1 else 1  # 對手
  hand = game_state[f"player{current_player}_hand"]
  other_player_health = game_state[f"player{other_player}_health"]

  if card_id in hand:
    # 找到卡牌並計算傷害值（這裡可以根據卡牌的屬性進行計算）
    damage = card_id
    # 更新對手的生命值
    other_player_health -= damage
    print(f'玩家{current_player}使用{card_id}造成傷害，玩家{other_player}生命剩下{other_player_health}點')

    if other_player_health <= 0:
      # 如果對手生命值小於等於0，遊戲結束，當前玩家獲勝
      game_state["winner"] = current_player
      print(f'遊戲結束，贏家為{current_player}')
    else:
      game_state["winner"] = None

    # 移除已經使用的卡牌
    hand.remove(card_id)
  else:
    print(f'WARN: {card_id} 不在玩家手牌中')

  # 更新遊戲狀態
  updated_state = {
    f"player{other_player}_health": other_player_health,
    f"player{current_player}_hand": hand,
    "current_player": other_player,  # 切換回合
    "winner": game_state["winner"],
  }
  return updated_state

# NOTE: 自動遊玩，測試用
def autoplay_card(game_state):
  current_player = game_state["current_player"]
  other_player = 2 if current_player == 1 else 1  # 對手
  hand = game_state[f"player{current_player}_hand"]
  other_player_health = game_state[f"player{other_player}_health"]

  if len(hand) == 0:
    print(f'ERRO: 玩家手牌為空')
    return None

  card_id = hand.pop() # 取出手牌最後一張
  # 找到卡牌並計算傷害值（這裡可以根據卡牌的屬性進行計算）
  damage = card_id
  # 更新對手的生命值
  other_player_health -= damage
  print(f'玩家{current_player}使用{card_id}造成傷害，玩家{other_player}生命剩下{other_player_health}點')

  if other_player_health <= 0:
    # 如果對手生命值小於等於0，遊戲結束，當前玩家獲勝
    game_state["winner"] = current_player
    print(f'遊戲結束，贏家為{current_player}')
  else:
    game_state["winner"] = None

  # 更新遊戲狀態
  updated_state = {
    f"player{other_player}_health": other_player_health,
    f"player{current_player}_hand": hand,
    "current_player": other_player,  # 切換回合
    "winner": game_state["winner"],
  }
  return updated_state

def is_game_over(game_state):
  return game_state["winner"] != None

# 將遊戲狀態以玩家視角輸出，過濾掉非公開資訊
def game_state_view_as(game_state, viewer_id):
  other_player = 2 if viewer_id == 1 else 1  # 對手
  game_data = {
    "playerHealth": game_state[f"player{viewer_id}_health"],
    "playerHand": game_state[f"player{viewer_id}_hand"],
    "opponentHealth": game_state[f"player{other_player}_health"],
  }
  return game_data

# 將抽牌的狀態更新發送給抽牌玩家
def draw_update_state(updated_state, player_id):
  game_data = {
    "playerHand": updated_state.get(f"player{player_id}_hand"),
  }
  return game_data

# 將出牌的狀態更新發送給指定玩家
def play_update_state(updated_state, current_player, viewer_id):
  other_player = 2 if current_player == 1 else 1  # 對手

  game_data = {}
  if current_player == viewer_id: # 行動玩家看他自己造成的狀態更新
    game_data["opponentHealth"] = updated_state[f"player{other_player}_health"]
    game_data["playerHand"] = updated_state[f"player{current_player}_hand"]

  else: # 對手看行動玩家造成的狀態更新
    game_data["playerHealth"] = updated_state[f"player{other_player}_health"]

  return game_data


if __name__ == "__main__":
  game_state = init_game() # 初始化遊戲
  turn = 1
  print(game_state)

  while not is_game_over(game_state):
    current_player = game_state['current_player']
    print(f'第{turn}回合，輪到玩家{current_player}，請按下 enter 表示玩家抽牌', end='')
    _ = input() # 模擬玩家行動

    updated_state = draw_card(game_state)
    game_state.update(updated_state)
    print(f"玩家{current_player}的手牌:", game_state[f"player{current_player}_hand"])

    # updated_state = play_card(game_state, game_state[f"player{current_player}_hand"][0])
    updated_state = autoplay_card(game_state) # 純自動模式
    
    game_state.update(updated_state)

    print("玩家1的生命值:", game_state["player1_health"])
    print("玩家2的生命值:", game_state["player2_health"])
    turn += 1

    # print(game_state)

