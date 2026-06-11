<script setup>
import { ref } from 'vue'
import MetaballIconTransition from './components/MetaballIconTransition.vue'

// ── SVG Icons (fill="currentColor" → inherits iconColor prop) ────

const svgPaw = `<svg width="360" height="360" viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M180 63.6602C224.832 63.6603 263.739 89.0199 283.164 126.176C304.636 140.917 349.613 180.64 336.183 213.88C327.175 236.175 302.248 242.01 282.178 235.671C262.442 271.818 224.085 296.34 180 296.34C135.158 296.34 96.2421 270.969 76.8213 233.8C55.3426 219.05 10.3934 179.339 23.8193 146.107C32.8274 123.812 57.7564 117.976 77.8271 124.316C97.5653 88.176 135.919 63.6602 180 63.6602ZM120.548 160.823C87.6668 149.65 77.2809 150.55 71.2207 165.55C68.1713 173.098 67.2675 181.293 67.8887 189.408C67.9736 190.434 68.0723 191.456 68.1846 192.474C70.0012 208.678 75.3274 224.279 83.7207 238.159C83.7004 238.148 83.6806 238.135 83.6602 238.124C103.365 270.714 139.138 292.5 180 292.5C222.416 292.5 259.347 269.024 278.516 234.358C278.511 234.357 278.507 234.355 278.503 234.354C250.361 222.984 224.69 207.773 224.613 207.728L224.569 207.7C222.725 206.754 157.757 173.465 120.548 160.823ZM180 67.5C137.588 67.5 100.659 90.97 81.4883 125.63C81.4918 125.631 81.4955 125.632 81.499 125.634C109.65 137.008 135.329 152.224 135.389 152.26L135.423 152.28C137.013 153.096 202.17 186.496 239.455 199.163C272.336 210.337 282.722 209.437 288.782 194.438C291.769 187.045 292.696 179.032 292.149 171.081C292.011 169.321 291.833 167.572 291.615 165.836C289.628 150.233 284.385 135.228 276.281 121.827C276.295 121.835 276.31 121.844 276.324 121.852C256.617 89.2755 220.852 67.5002 180 67.5Z" fill="currentColor"/>
</svg>`

const svgWifi = `<svg width="360" height="360" viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M242.184 206.208C233.856 234.648 214.104 255.12 182.736 256.272C182.976 204.48 191.232 183.072 234.552 182.232V177.816H182.184V103.728C213.864 104.64 233.808 125.208 242.184 153.816C244.872 162.96 253.464 169.104 262.992 169.104H300C300 108.936 246.192 60 180 60C113.808 60 60 108.936 60 169.08H97.008C106.536 169.08 115.152 162.936 117.816 153.792C126.144 125.352 145.896 104.88 177.264 103.728C177.024 155.52 168.768 176.928 125.448 177.768V182.184H177.816V256.272C146.136 255.36 126.192 234.792 117.816 206.184C115.128 197.04 106.536 190.896 97.008 190.896H60C60 251.04 113.832 299.976 180 299.976C246.168 299.976 300 251.04 300 190.896H262.992C253.464 190.896 244.848 197.04 242.184 206.184V206.208Z" fill="currentColor"/>
</svg>`

const svgStar = `<svg width="360" height="360" viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M180 30L225.6 124.2L330 139.2L255 212.4L272.4 316.2L180 267.6L87.6 316.2L105 212.4L30 139.2L134.4 124.2L180 30Z" fill="currentColor"/>
</svg>`

const svgHeart = `<svg width="360" height="360" viewBox="0 0 360 360" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M180 315L155.7 292.8C99 241.2 45 192.6 45 133.5C45 85.5 83.4 47.1 131.4 47.1C158.4 47.1 184.5 60 180 84.6C175.5 60 201.6 47.1 228.6 47.1C276.6 47.1 315 85.5 315 133.5C315 192.6 261 241.2 204.3 292.8L180 315Z" fill="currentColor"/>
</svg>`

const svgIconSet = [svgPaw, svgWifi, svgStar, svgHeart]
const svgIconNames = ['掌印 Paw', 'WiFi', '星 Star', '心 Heart']
const svgIconColors = ['#1a1a2e', '#4C5FF0', '#e8a020', '#e04060']

const svgIndex = ref(0)

// ── Easing comparison ────────────────────────────────────────────
const compareIndex = ref(0)
const compareIcons = [svgPaw, svgWifi, svgStar, svgHeart]

// ── Size scaling ─────────────────────────────────────────────────
const sizeIndex = ref(0)
const sizeIcons = [svgPaw, svgWifi, svgStar, svgHeart]

// ── Navigation ───────────────────────────────────────────────────
function nextSvg() { svgIndex.value = (svgIndex.value + 1) % svgIconSet.length }
function prevSvg() { svgIndex.value = (svgIndex.value - 1 + svgIconSet.length) % svgIconSet.length }
function nextCompare() { compareIndex.value = (compareIndex.value + 1) % compareIcons.length }
function nextSize() { sizeIndex.value = (sizeIndex.value + 1) % sizeIcons.length }

// ── Auto-cycle ───────────────────────────────────────────────────
const autoCycle = ref(false)
let cycleTimer = null

function toggleAutoCycle() {
  autoCycle.value = !autoCycle.value
  if (autoCycle.value) {
    cycleTimer = setInterval(() => {
      svgIndex.value = (svgIndex.value + 1) % svgIconSet.length
      compareIndex.value = (compareIndex.value + 1) % compareIcons.length
      sizeIndex.value = (sizeIndex.value + 1) % sizeIcons.length
    }, 2500)
  } else {
    clearInterval(cycleTimer)
    cycleTimer = null
  }
}
</script>

<template>
  <div class="demo-page">
    <header class="demo-header">
      <h1>Metaball Icon Transition</h1>
      <p class="subtitle">Web 版融球风格图标切换 — CSS Filter blur + contrast</p>
    </header>

    <!-- ====== Section 0: Static Icon Gallery ====== -->
    <section class="demo-section">
      <h2>项目图标集</h2>
      <p class="section-desc">静态展示全部 4 个 SVG 图标（你上传的掌印 / WiFi + 补充星 / 心）</p>
      <div class="gallery">
        <div
          v-for="(svg, i) in svgIconSet"
          :key="i"
          class="gallery-item"
        >
          <div
            class="gallery-icon"
            :style="{ color: svgIconColors[i] }"
            v-html="svg"
          />
          <span class="gallery-label">{{ svgIconNames[i] }}</span>
        </div>
      </div>
    </section>

    <!-- ====== Section 1: Metaball Transition ====== -->
    <section class="demo-section">
      <h2>Metaball 融合过渡</h2>
      <p class="section-desc">自然融合缓动 · 140px · preserveColor 模式 · 掌印 ⇄ WiFi ⇄ 星 ⇄ 心</p>
      <div class="demo-row">
        <button class="nav-btn" @click="prevSvg">◀</button>
        <div class="icon-stage-main">
          <MetaballIconTransition
            v-model="svgIndex"
            :icons="svgIconSet"
            :size="140"
            :duration="700"
            :max-blur="20"
            :contrast-strength="25"
            easing="cubic-bezier(0.65,0,0.35,1)"
            background-color="#ffffff"
            icon-color="#1a1a2e"
            :preserve-color="true"
          />
        </div>
        <button class="nav-btn" @click="nextSvg">▶</button>
      </div>
      <div class="icon-indicators">
        <span
          v-for="(name, i) in svgIconNames"
          :key="i"
          :class="['indicator-text', { active: i === svgIndex }]"
          @click="svgIndex = i"
        >{{ name }}</span>
      </div>
    </section>

    <!-- ====== Section 2: CSS vs SVG Filter Mode Comparison ====== -->
    <section class="demo-section">
      <h2>滤镜模式对比：CSS overlay vs SVG feColorMatrix</h2>
      <p class="section-desc">
        同参数、同图标、同色。左侧 CSS overlay 硬边 GPU 加速，右侧 SVG 柔边架构直白。
      </p>
      <div class="comparison-grid" style="grid-template-columns:1fr 1fr;"> 
        <div class="comparison-item">
          <span class="comparison-label">CSS overlay</span>
          <MetaballIconTransition
            :current-index="compareIndex"
            :icons="compareIcons"
            :size="80"
            :duration="700"
            :max-blur="14"
            :contrast-strength="22"
            easing="cubic-bezier(0.65,0,0.35,1)"
            icon-color="#4C5FF0"
            background-color="#ffffff"
            :preserve-color="true"
            filter-mode="css"
          />
        </div>
        <div class="comparison-item">
          <span class="comparison-label">SVG feColorMatrix</span>
          <MetaballIconTransition
            :current-index="compareIndex"
            :icons="compareIcons"
            :size="80"
            :duration="700"
            :max-blur="14"
            :contrast-strength="22"
            easing="cubic-bezier(0.65,0,0.35,1)"
            icon-color="#4C5FF0"
            background-color="#ffffff"
            :preserve-color="true"
            filter-mode="svg"
          />
        </div>
      </div>
      <button class="btn btn-sm" @click="nextCompare">切换 ↻</button>
    </section>

    <!-- ====== Section 3: Easing Comparison ====== -->
    <section class="demo-section">
      <h2>缓动曲线对比</h2>
      <p class="section-desc">
        四种缓动并排对比 — 点击下方按钮同时切换全部
      </p>
      <div class="comparison-grid">
        <div class="comparison-item" v-for="(conf, name) in {
          '弹性 Q 弹': { easing: 'cubic-bezier(0.34,1.56,0.64,1)', color: '#4C5FF0' },
          '自然融合': { easing: 'cubic-bezier(0.65,0,0.35,1)', color: '#1a1a2e' },
          'ease-in-out': { easing: 'ease-in-out', color: '#e8a020' },
          'linear': { easing: 'linear', color: '#e04060' },
        }" :key="name">
          <span class="comparison-label">{{ name }}</span>
          <MetaballIconTransition
            :current-index="compareIndex"
            :icons="compareIcons"
            :size="70"
            :duration="800"
            :max-blur="12"
            :contrast-strength="20"
            :easing="conf.easing"
            :icon-color="conf.color"
            background-color="#ffffff"
            :preserve-color="true"
          />
        </div>
      </div>
      <button class="btn btn-sm" @click="nextCompare">切换全部 ↻</button>
    </section>

    <!-- ====== Section 4: Size Scaling ====== -->
    <section class="demo-section">
      <h2>尺寸缩放</h2>
      <p class="section-desc">48 / 64 / 80 / 100 / 128 px，Metaball 效果自适应 — 点击按钮同时切换</p>
      <div class="size-grid">
        <MetaballIconTransition
          v-for="s in [48, 64, 80, 100, 128]"
          :key="s"
          :current-index="sizeIndex"
          :icons="sizeIcons"
          :size="s"
          :duration="600"
          :max-blur="Math.round(s * 0.15)"
          :contrast-strength="20"
          easing="cubic-bezier(0.34,1.56,0.64,1)"
          icon-color="#1a1a2e"
          background-color="#ffffff"
          :preserve-color="true"
          :style="{ margin: '0 8px' }"
        />
      </div>
      <button class="btn btn-sm" @click="nextSize">切换全部 ↻</button>
    </section>

    <!-- ====== Auto-cycle ====== -->
    <section class="demo-section auto-section">
      <button
        :class="['btn', 'btn-lg', autoCycle ? 'btn-active' : '']"
        @click="toggleAutoCycle"
      >
        {{ autoCycle ? '⏸ 停止自动轮播' : '▶ 自动轮播全部区域' }}
      </button>
    </section>

    <!-- ====== Section 5: Technical Notes ====== -->
    <section class="demo-section notes">
      <h2>技术原理速览</h2>
      <div class="notes-content">
        <div class="note-card">
          <h3>🔬 blur + contrast = 融球</h3>
          <p>
            两个图标 opacity 交叉淡入淡出时空间重叠。
            <code>blur(Npx)</code> 让边缘 alpha 连续渐变，
            <code>contrast(C)</code> 以 0.5 为阈值二值化 —
            重叠区 alpha 叠加突破阈值连通，分离区被裁切断开。
          </p>
        </div>
        <div class="note-card">
          <h3>⚡ CSS Filter 由 GPU 加速</h3>
          <p>
            <code>filter: blur() contrast()</code> 由 GPU 合成器处理，
            一行 CSS 等效 SVG <code>feGaussianBlur</code> +
            <code>feColorMatrix</code>，Web 端 Metaball 最优解。
          </p>
        </div>
        <div class="note-card">
          <h3>📐 三角波 drive blur</h3>
          <p>
            <code>factor = 1 − |2p − 1|</code>：progress 0/1 时 blur=0
            图标锐利，progress=0.5 时 blur=max 融合峰值。contrast 同步跟随。
          </p>
        </div>
      </div>
    </section>

    <footer class="demo-footer">
      <p>MetaballIconTransition v1.0 — Vue3 Composition API · 零依赖 · MIT</p>
    </footer>
  </div>
</template>

<style scoped>
/* ── Demo Page ─────────────────────────────────────────────────── */
.demo-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.demo-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.demo-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: #666;
}

/* ── Gallery (static icons) ──────────────────────────────────── */
.gallery {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
  padding: 1.5rem 0;
}

.gallery-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.gallery-icon {
  width: 80px;
  height: 80px;
}

.gallery-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.gallery-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #888;
}

/* ── Buttons ──────────────────────────────────────────────────── */
.btn {
  padding: 0.6rem 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  color: #1a1a2e;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover { border-color: #4C5FF0; color: #4C5FF0; }
.btn-active { background: #4C5FF0; color: #fff; border-color: #4C5FF0; }
.btn-sm { padding: 0.4rem 1rem; font-size: 0.8rem; margin-top: 0.75rem; }
.btn-lg { padding: 0.75rem 2rem; font-size: 1rem; }

.nav-btn {
  width: 48px;
  height: 48px;
  border: 2px solid #e8e8e8;
  border-radius: 50%;
  background: #fff;
  font-size: 1.2rem;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-btn:hover { border-color: #4C5FF0; color: #4C5FF0; background: #f5f7ff; }

/* ── Sections ──────────────────────────────────────────────────── */
.demo-section {
  margin-bottom: 3rem;
}

.demo-section h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.section-desc {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 1rem;
}

.demo-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.icon-stage-main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 160px;
  min-height: 160px;
}

.icon-indicators {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.indicator-text {
  padding: 0.35rem 0.9rem;
  border-radius: 20px;
  background: #f0f0f0;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  color: #666;
  transition: all 0.2s;
}

.indicator-text.active { background: #4C5FF0; color: #fff; }

/* ── Comparison Grid ──────────────────────────────────────────── */
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.comparison-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #eee;
}

.comparison-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Size Grid ────────────────────────────────────────────────── */
.size-grid {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 1rem 0;
}

.auto-section {
  text-align: center;
}

/* ── Notes ────────────────────────────────────────────────────── */
.notes {
  background: #fafbfc;
  border-radius: 16px;
  padding: 1.5rem;
}

.notes-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.note-card {
  background: #fff;
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid #eee;
}

.note-card h3 {
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1a1a2e;
}

.note-card p {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.6;
}

.note-card code {
  background: #f0f2f5;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.85em;
  color: #4C5FF0;
}

/* ── Footer ──────────────────────────────────────────────────── */
.demo-footer {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid #eee;
  color: #aaa;
  font-size: 0.8rem;
}

/* ── Responsive ────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .comparison-grid { grid-template-columns: repeat(2, 1fr); }
  .demo-header h1 { font-size: 1.5rem; }
}
</style>
