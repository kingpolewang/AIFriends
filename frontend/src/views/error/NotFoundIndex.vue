<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const canvasRef = ref(null);
const score = ref(0);
const gameOver = ref(false);

// 游戏配置
let ctx, animationFrame;
let paddle = { x: 0, y: 0, width: 80, height: 10 };
let ball = { x: 0, y: 0, dx: 4, dy: -4, radius: 8 };

const initGame = () => {
  const canvas = canvasRef.value;
  ctx = canvas.getContext('2d');
  canvas.width = 400;
  canvas.height = 300;

  paddle.x = (canvas.width - paddle.width) / 2;
  paddle.y = canvas.height - 20;
  resetBall();
};

const resetBall = () => {
  ball.x = canvasRef.value.width / 2;
  ball.y = canvasRef.value.height - 30;
  ball.dx = (Math.random() - 0.5) * 8;
  ball.dy = -4;
  gameOver.value = false;
  score.value = 0;
};

const draw = () => {
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  // 画球
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
  ctx.fillStyle = "#646cff";
  ctx.fill();
  ctx.closePath();

  // 画挡板
  ctx.fillStyle = "#42b883";
  ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);

  // 碰撞检测：左右墙壁
  if (ball.x + ball.dx > canvasRef.value.width - ball.radius || ball.x + ball.dx < ball.radius) {
    ball.dx = -ball.dx;
  }
  // 碰撞检测：顶部
  if (ball.y + ball.dy < ball.radius) {
    ball.dy = -ball.dy;
  }
  // 碰撞检测：底部/挡板
  else if (ball.y + ball.dy > paddle.y - ball.radius) {
    if (ball.x > paddle.x && ball.x < paddle.x + paddle.width) {
      ball.dy = -ball.dy;
      ball.dy *= 1.05; // 逐渐加速
      score.value++;
    } else {
      gameOver.value = true;
      return;
    }
  }

  ball.x += ball.dx;
  ball.y += ball.dy;
  animationFrame = requestAnimationFrame(draw);
};

const handleMouseMove = (e) => {
  const rect = canvasRef.value.getBoundingClientRect();
  const rootX = e.clientX - rect.left;
  paddle.x = Math.max(0, Math.min(rootX - paddle.width / 2, canvasRef.value.width - paddle.width));
};

const restart = () => {
  resetBall();
  draw();
};

const goHome = () => {
  router.push('/');
};

onMounted(() => {
  initGame();
  draw();
});

onUnmounted(() => {
  cancelAnimationFrame(animationFrame);
});
</script>

<template>
  <div class="error-container">
    <h1 class="code">404</h1>
    <p class="msg">糟糕！你来到了荒芜之地。别急着走，接个球吧？</p>

    <div class="game-box">
      <div class="score">得分: {{ score }}</div>
      <canvas
        ref="canvasRef"
        @mousemove="handleMouseMove"
        :class="{ 'game-over-blur': gameOver }"
      ></canvas>

      <div v-if="gameOver" class="overlay">
        <h3>游戏结束</h3>
        <button @click="restart" class="btn-play">再来一局</button>
      </div>
    </div>

    <button @click="goHome" class="btn-home">带我回家</button>
  </div>
</template>

<style scoped>
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  font-family: 'Inter', system-ui, sans-serif;
  background: #1a1a1a;
  color: white;
  text-align: center;
}

.code {
  font-size: 8rem;
  margin: 0;
  background: linear-gradient(135deg, #42b883, #646cff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
}

.msg {
  color: #888;
  margin-bottom: 2rem;
}

.game-box {
  position: relative;
  border: 2px solid #333;
  border-radius: 8px;
  background: #000;
  overflow: hidden;
  cursor: none; /* 隐藏鼠标，增强沉浸感 */
}

.score {
  position: absolute;
  top: 10px;
  right: 15px;
  color: #42b883;
  font-weight: bold;
}

.game-over-blur {
  filter: blur(4px);
}

.overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: transform 0.2s;
}

.btn-play {
  background: #42b883;
  color: white;
}

.btn-home {
  margin-top: 2rem;
  background: transparent;
  border: 1px solid #646cff;
  color: #646cff;
}

button:hover {
  transform: scale(1.05);
}
</style>