// 初始化之後
const gameData1 = {
  playerHealth: 50,
  playerHand: [2],
  opponentHealth: 50
}

// 抽牌
const gameData2 = {
  playerHand: [2,5],
}

// 出牌
const gameData3 = {
  playerHand: [2],
  opponentHealth: 45
}

// 將遊戲資訊的 JSON 資料更新到頁面上
function updateGameInfo(gameData) {
  // 更新玩家血量
  if (gameData.playerHealth) document.getElementById("player-health").textContent = gameData.playerHealth
    
  // 更新玩家手牌數
  if (gameData.playerHand) document.getElementById("player-hand").textContent = gameData.playerHand.join(', ')
    
  // 更新對手血量
  if (gameData.opponentHealth) document.getElementById("opponent-health").textContent = gameData.opponentHealth
}

// 在前端頁面新增內容，後期無用
const sendChatMessage = () => {
  const messageInput = document.getElementById("message-input");
  const message = messageInput.value;
  if (message.trim() !== "") {
    sendMessage('chat', { message })
    // 清空輸入欄位
    messageInput.value = "";
  }
}

// 處理送出按鈕的點擊事件
document.getElementById("send-button").addEventListener("click", sendChatMessage)
document.getElementById("message-input").addEventListener('keydown', (e) => {
  // console.log(e.code)
  if (e.code === 'Enter' || e.code === 'NumpadEnter') sendChatMessage()
}, false);

const ws = new WebSocket("ws://shrouded-castle-56322-ddcaf8d0cc91.herokuapp.com/")
var messages = document.getElementById("messages");

function showMessage(message, type='info') {
  const p = document.createElement("p");
  let fixedMessage
  switch(type) {
    case 'error':
      fixedMessage = `[錯誤] ${message}`
      break
    case 'sys':
      fixedMessage = `[通知] ${message}`
      break
    case 'info':
    default:
      fixedMessage = message
  }

  p.textContent = fixedMessage;
  messages.appendChild(p);
  messages.scrollTop = messages.scrollHeight; // 捲動置底
}

// 跟 websocket 溝通的最底層
function sendMessage(action, payload = null) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    var message = JSON.stringify({ action: action, payload: payload });
    ws.send(message);
  } else {
    showMessage("WebSocket not connected.", "error");
  }
}

function createRoom() {
  sendMessage('create_room')
}

function joinRoom() {
  var room_id = parseInt(prompt("Enter room ID:"));
  if (isNaN(room_id)) {
    showMessage("room_id is not number.", "error");
    return
  }
  sendMessage('join_room', { room_id: room_id });
}

function startGame() {
  var room_id = parseInt(prompt("Enter room ID to start the game:"));
  if (isNaN(room_id)) {
    showMessage("room_id is not number.", "error");
    return
  }
  sendMessage('start_game', { room_id: room_id });
}

function playerDrawCard() {
  sendMessage('player_draw_card')
}

function playerPlayCard() {
  sendMessage('player_play_card')
}

function handlGameEvent(payload) {
  const { message, gameEvent, gameData } = payload

  switch(gameEvent) {
    case 'setState':
      showMessage(message, 'sys')
      updateGameInfo(gameData)
      break
    case 'turnStart':
      showMessage(message, 'sys')
      break
    case 'waitOther':
      showMessage(message, 'sys')
      break
    case 'gameOver':
      showMessage(message, 'sys')
      break
  }
}

ws.onmessage = function(event) {
  const data = JSON.parse(event.data)

  if (data.gameEvent) {
    handlGameEvent(data)
  } else if (data.error) {
    showMessage(data.message, 'error')
  } else {
    showMessage(data.message, 'info')
  }
}
