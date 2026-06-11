<script setup>
/**
 * MetaballIconTransition.vue
 *
 * Web 版 Metaball / 融球风格图标切换动画组件。
 *
 * 双滤镜模式：
 *
 *   filterMode='css'（默认）：
 *     CSS filter: blur(Xpx) contrast(Y) + overlay mix-blend-mode:lighten
 *     图标纯黑渲染 → blur+contrast 产出 Metaball 形状 →
 *     独立 overlay 层 lighten 混合着色。
 *     优点：GPU 加速、边缘硬朗、性能最佳。
 *     缺点：需要 overlay 着色层，架构略迂回。
 *
 *   filterMode='svg'：
 *     SVG feGaussianBlur + feColorMatrix(仅 alpha 通道)
 *     R/G/B identity 直通保留原色，仅 alpha 做高斜率线性映射阈值化。
 *     优点：图标直接用 iconColor 渲染，架构直白，无需黑化+着色。
 *     缺点：边缘带柔光晕（blur 混入背景白），SVG filter 非 GPU 加速，
 *           动态更新需 v-html 整段替换（每帧重新 parse filter DOM）。
 *
 *   两种模式下 blur / contrast(或 slope/intercept) 均通过三角波跟随
 *   progress 动态变化。
 */

import { ref, computed, watch, onBeforeUnmount } from 'vue'

// ── Props ────────────────────────────────────────────────────────
const props = defineProps({
  icons:          { type: Array,   default: () => [] },
  modelValue:     { type: Number,  default: undefined },
  currentIndex:   { type: Number,  default: 0 },
  size:           { type: Number,  default: 80 },
  duration:       { type: Number,  default: 600 },
  maxBlur:        { type: Number,  default: 14 },
  contrastStrength:{ type: Number, default: 22 },
  preserveColor:  { type: Boolean, default: false },

  /**
   * 滤镜模式：
   *   'css' — CSS blur+contrast + overlay lighten（默认，硬边 GPU 加速）
   *   'svg' — SVG feGaussianBlur + feColorMatrix(A only)（柔边，架构直白）
   */
  filterMode:     { type: String,  default: 'css' },
  easing:         { type: String,  default: 'cubic-bezier(0.34,1.56,0.64,1)' },
  backgroundColor:{ type: String,  default: '#ffffff' },
  iconColor:      { type: String,  default: '#1a1a2e' },
})

const emit = defineEmits(['update:modelValue'])

// ── Unique filter ID（SVG 模式使用） ─────────────────────────────
let _fid = 0
const svgFilterId = computed(() => `mb-svg-${++_fid}`)
// 稳定引用：首次计算后固定
const stableFilterId = ref('')
if (!stableFilterId.value) stableFilterId.value = `mb-svg-${Math.random().toString(36).slice(2, 8)}`

// ── State ─────────────────────────────────────────────────────────
const activeIndex = computed(() =>
  props.modelValue !== undefined ? props.modelValue : props.currentIndex
)
const displayIndex = ref(activeIndex.value)
const prevIndex    = ref(activeIndex.value)
const progress     = ref(0)
const isAnimating  = ref(false)

let rafId = null
let startTime = 0

// ── Easing ────────────────────────────────────────────────────────
const easingPresets = {
  'linear':      t => t,
  'ease-in':     t => t * t * t,
  'ease-out':    t => 1 - Math.pow(1 - t, 3),
  'ease-in-out': t => t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2,
}

function createCubicBezier(x1, y1, x2, y2) {
  const sx  = t => { const m=1-t; return 3*m*m*t*x1 + 3*m*t*t*x2 + t*t*t }
  const sxd = t => { const m=1-t; return 3*m*m*x1 + 6*m*t*(x2-x1) + 3*t*t*(1-x2) }

  const solveX = (x, e=1e-7) => {
    let t = x
    for (let i=0; i<8; i++) { const d=sx(t)-x; if (Math.abs(d)<e) return t; const dd=sxd(t); if (Math.abs(dd)<1e-6) break; t-=d/dd }
    let lo=0, hi=1; t=x
    while (lo<hi) { const d=sx(t)-x; if (Math.abs(d)<e) return t; if (x>d) lo=t; else hi=t; t=(hi-lo)/2+lo }
    return t
  }
  return x => { if (x<=0) return 0; if (x>=1) return 1; const t=solveX(x); const m=1-t; return 3*m*m*t*y1 + 3*m*t*t*y2 + t*t*t }
}

function resolveEasing(s) {
  if (easingPresets[s]) return easingPresets[s]
  const m = s.match(/cubic-bezier\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)/)
  if (m) return createCubicBezier(+m[1], +m[2], +m[3], +m[4])
  return easingPresets['ease-in-out']
}

const easeFn = computed(() => resolveEasing(props.easing))

// ── Animation ─────────────────────────────────────────────────────

function cancel() { if (rafId!==null) { cancelAnimationFrame(rafId); rafId=null } }

function startTransition(from, to) {
  cancel()
  prevIndex.value   = from
  displayIndex.value= to
  progress.value    = 0
  isAnimating.value = true
  startTime         = 0
  const ease = easeFn.value
  function tick(ts) {
    if (!startTime) startTime = ts
    const raw = Math.min((ts - startTime) / props.duration, 1)
    progress.value = ease(raw)
    if (raw < 1) { rafId = requestAnimationFrame(tick) }
    else { progress.value=1; isAnimating.value=false; prevIndex.value=to; rafId=null }
  }
  rafId = requestAnimationFrame(tick)
}

watch(activeIndex, (nv, ov) => {
  if (nv === ov) return
  if (isAnimating.value) { cancel(); startTransition(displayIndex.value, nv) }
  else { startTransition(ov ?? displayIndex.value, nv) }
  emit('update:modelValue', nv)
})

// ── Computed ──────────────────────────────────────────────────────

const factor = computed(() => { const p=progress.value; return 1-Math.abs(2*p-1) })
const blurPx = computed(() => props.maxBlur * factor.value)
const contrastVal = computed(() => 1 + (props.contrastStrength - 1) * factor.value)

const containerStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
}))

/**
 * preserveColor=true:
 *   Mask 层：图标纯黑渲染 → CSS blur+contrast → 产出 Metaball 形状。
 *   颜色由独立的 overlay 层通过 mix-blend-mode: lighten 注入。
 */
const maskFilter = computed(() =>
  `blur(${blurPx.value.toFixed(1)}px) contrast(${contrastVal.value.toFixed(1)})`
)

const stageStyle = computed(() => {
  // SVG filter 模式
  if (props.filterMode === 'svg') {
    return {
      background: props.backgroundColor,
      filter: `url(#${stableFilterId.value})`,
    }
  }
  // CSS preserveColor 模式
  if (props.preserveColor) {
    return {
      background: props.backgroundColor,
      filter: maskFilter.value,
    }
  }
  // CSS grayscale 模式
  return {
    background: props.backgroundColor,
    filter: `blur(${blurPx.value.toFixed(1)}px) grayscale(1) contrast(${contrastVal.value.toFixed(1)})`,
  }
})

/**
 * preserveColor 时图标强制纯黑，颜色由 overlay lighten 注入。
 * 非 preserveColor / SVG 模式时使用 iconColor 直接渲染。
 */
const iconStyle = computed(() => {
  if (props.preserveColor && props.filterMode === 'css') {
    return { color: '#000000', fill: '#000000', fontSize: `${props.size * 0.6}px`, lineHeight: 1 }
  }
  return { color: props.iconColor, fill: props.iconColor, fontSize: `${props.size * 0.6}px`, lineHeight: 1 }
})

// ── SVG filter 模式 ──────────────────────────────────────────────

/** feColorMatrix 的 slope / intercept（等价于 CSS contrast） */
const svgSlope = computed(() => 1 + (props.contrastStrength - 1) * factor.value)
const svgIntercept = computed(() => 0.5 * (1 - svgSlope.value))

/**
 * 生成完整 SVG filter 标记字符串。
 * 每帧 progress 变化时 computed 重新求值 → v-html 完整替换 DOM
 * → 浏览器重新 parse filter，确保参数更新生效。
 */
const svgFilterMarkup = computed(() => {
  const b = blurPx.value.toFixed(1)
  const s = svgSlope.value.toFixed(2)
  const i = svgIntercept.value.toFixed(2)
  return `<svg xmlns="http://www.w3.org/2000/svg">
  <filter id="${stableFilterId.value}" color-interpolation-filters="sRGB">
    <feGaussianBlur in="SourceGraphic" stdDeviation="${b}" result="blur" />
    <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 ${s} ${i}" />
  </filter>
</svg>`
})

// ── Helpers ──────────────────────────────────────────────────────

function isFullSvg(s)  { return typeof s==='string' && /^\s*<svg\b/.test(s.trim()) }
function isSvgPath(s)  { return typeof s==='string' && /^<path\b|^<circle\b|^<rect\b|^M\s*[\d.]/.test(s.trim()) }

onBeforeUnmount(() => cancel())
</script>

<template>
  <div class="metaball-icon-transition" :style="containerStyle">

    <!-- SVG filter 定义（filterMode='svg' 时生效） -->
    <div
      v-if="filterMode === 'svg'"
      class="metaball-svg-filter"
      aria-hidden="true"
      v-html="svgFilterMarkup"
    />

    <div class="metaball-stage" :style="stageStyle">

      <!-- Prev icon (fading out) -->
      <div
        v-if="isAnimating && prevIndex !== displayIndex"
        class="icon-layer"
        :style="[iconStyle, { opacity: 1 - progress }]"
      >
        <slot :name="`icon-${prevIndex}`" :icon="icons[prevIndex]" :index="prevIndex" :is-active="false">
          <slot name="icon" :icon="icons[prevIndex]" :index="prevIndex" :is-active="false">
            <template v-if="isFullSvg(icons[prevIndex])">
              <div class="icon-svg-full" :style="{ width: size*0.7+'px', height: size*0.7+'px' }" v-html="icons[prevIndex]" />
            </template>
            <template v-else-if="isSvgPath(icons[prevIndex])">
              <svg :width="size*0.7" :height="size*0.7" viewBox="0 0 24 24" :fill="iconStyle.fill" v-html="icons[prevIndex]" />
            </template>
            <span v-else>{{ icons[prevIndex] }}</span>
          </slot>
        </slot>
      </div>

      <!-- Current icon (fading in / static) -->
      <div class="icon-layer" :style="[iconStyle, { opacity: isAnimating ? progress : 1 }]">
        <slot :name="`icon-${displayIndex}`" :icon="icons[displayIndex]" :index="displayIndex" :is-active="true">
          <slot name="icon" :icon="icons[displayIndex]" :index="displayIndex" :is-active="true">
            <template v-if="isFullSvg(icons[displayIndex])">
              <div class="icon-svg-full" :style="{ width: size*0.7+'px', height: size*0.7+'px' }" v-html="icons[displayIndex]" />
            </template>
            <template v-else-if="isSvgPath(icons[displayIndex])">
              <svg :width="size*0.7" :height="size*0.7" viewBox="0 0 24 24" :fill="iconStyle.fill" v-html="icons[displayIndex]" />
            </template>
            <span v-else>{{ icons[displayIndex] }}</span>
          </slot>
        </slot>
      </div>

    </div>

    <!-- Color overlay（仅 CSS preserveColor 模式生效） -->
    <div
      v-if="preserveColor && filterMode === 'css'"
      class="metaball-color-overlay"
      :style="{ background: iconColor }"
    />
  </div>
</template>

<style scoped>
.metaball-icon-transition {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 12px;
  user-select: none;
  -webkit-user-select: none;
}

.metaball-stage {
  position: absolute;
  inset: 0;
  will-change: filter;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}

.icon-layer {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-layer span {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.icon-svg-full {
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-svg-full :deep(svg) {
  width: 100%;
  height: 100%;
  display: block;
}

/* SVG filter 定义容器：不可见，仅存放 filter DOM */
.metaball-svg-filter {
  position: absolute;
  width: 0;
  height: 0;
  overflow: hidden;
  pointer-events: none;
}

/* preserveColor 颜色叠层：覆盖在 mask 上，仅对黑色区域着色 */
.metaball-color-overlay {
  position: absolute;
  inset: 0;
  mix-blend-mode: lighten;
  pointer-events: none;
  border-radius: inherit;
}
</style>
