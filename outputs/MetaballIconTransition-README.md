# MetaballIconTransition

> Vue3 Composition API 组件 — Web 版融球（Metaball）风格图标切换动画

两个图标切换时，不是普通的 opacity 淡入淡出，而是在切换中段产生类似**液体融合、拉伸、连接、断开**的 Metaball 效果。边缘圆润、自然、有弹性：开始和结束时图标保持锐利清晰，中间阶段融合感最强。

---

## 最终架构

### preserveColor=true（推荐，适合彩色图标）

三层 CSS 架构，全部 GPU 加速，零 SVG filter 依赖：

```
┌─ Container（透明背景，overflow:hidden，border-radius）──────┐
│                                                             │
│  ┌─ Mask 层（bg:white; filter: blur(Xpx) contrast(Y)）──┐   │
│  │  Icon A（fill=#000 纯黑, opacity: 1→0）              │   │
│  │  Icon B（fill=#000 纯黑, opacity: 0→1）              │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                │
│         blur + contrast 产出 Metaball 形状                  │
│         （黑色液体 blob / 白色背景）                          │
│                                                             │
│  ┌─ Overlay 层（bg:iconColor;                              │
│  │             mix-blend-mode: lighten）────────────────┐   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓                                │
│    lighten(黑, iconColor) → iconColor  ← 着色              │
│    lighten(白, iconColor) → 白色        ← 背景不变          │
└─────────────────────────────────────────────────────────────┘
```

**关键设计决策**：

- **图标强制纯黑渲染**（`#000000`）：R=G=B=0，CSS `contrast()` 逐通道处理时三通道完全同步，从根本上杜绝色偏。
- **颜色由独立 overlay 注入**（`mix-blend-mode: lighten`）：不污染容器背景，不会被 `border-radius` 裁剪泄漏。
- **overlay 与 mask 同层等大**，共享同一 `overflow:hidden` + `border-radius` 裁剪区，无色块泄漏。
- **filter 值与 V1 完全一致**：`blur(Xpx) contrast(Y)`，不插 `grayscale(1)`。

### preserveColor=false（灰度模式）

```css
filter: blur(Xpx) grayscale(1) contrast(Y)
```

适合不在意颜色保留的场景（如单纯的黑白 icon）。`grayscale(1)` 强制 R=G=B，杜绝色偏但牺牲颜色。

---

## 问题演进与解决方案

### 问题 1：黑色图标切换出现蓝边

**现象**：`iconColor="#1a1a2e"`（RGB=26,26,46）的两个图标切换时，过渡边缘出现明显蓝色。

**根因**：CSS `contrast()` 对 R/G/B/A 四通道**独立处理**。`#1a1a2e` 蓝通道（46）高于红/绿（26）。模糊后边缘各通道都在 0.5 阈值附近，蓝通道因其起点更高而率先跨越阈值，被 contrast 放大为可见蓝色边缘。

```
contrast(C) 公式：newValue = (oldValue - 0.5) × C + 0.5

oldR=0.48 → newR = (0.48-0.5)×22+0.5 = 0.06（近黑）
oldB=0.52 → newB = (0.52-0.5)×22+0.5 = 0.94（近纯蓝）← 色偏源
```

**尝试过的方案**：

| 方案 | 结果 | 原因 |
|------|------|------|
| 插入 `grayscale(1)` | ❌ 全部变灰 | 消灭色偏也消灭了所有颜色 |
| SVG `feComponentTransfer`（仅 A 通道 identity） | ❌ 边缘发糊 | RGB 直通保留模糊混色，产生光晕而非硬边；且 Vue 响应式在 SVG filter 子元素上无法可靠触发浏览器重算 |
| SVG `feColorMatrix` + 命令式 DOM | ❌ 同上 | 浏览器 filter 缓存问题依然存在，且无 GPU 加速 |
| `mix-blend-mode: screen` 着色 | ❌ 黑框泄漏 | 颜色放容器 background 上，border-radius 裁剪后四角露出彩色 |

**最终方案**：图标纯黑渲染 + overlay `mix-blend-mode: lighten` 着色（见上方架构图）。

### 问题 2：`v-model` 与 `:current-index` 互斥导致动画不触发

**现象**：使用 `:current-index`（非 v-model）时，切换索引不触发动画。

**根因**：`modelValue` 默认值 `0` 导致 `0 ?? currentIndex` 永远返回 `0`（`0` 不是 nullish）。

**修复**：
```js
// ❌ 旧
modelValue: { type: Number, default: 0 }
const activeIndex = computed(() => props.modelValue ?? props.currentIndex)

// ✅ 新
modelValue: { type: Number, default: undefined }
const activeIndex = computed(() =>
  props.modelValue !== undefined ? props.modelValue : props.currentIndex
)
```

### 问题 3：SVG 图标 `fill="white"` + 白背景 = 不可见

**现象**：用户上传的 SVG 图标 `fill="white"` 写死在 `<path>` 上，容器背景也是白色，白图标放白底完全看不见。

**修复**：将 SVG 内 `fill="white"` 替换为 `fill="currentColor"`，由组件 CSS `color` 属性控制颜色。

### 问题 4：`border-radius` 裁剪 + `mix-blend-mode` 导致黑框泄漏

**现象**：preserveColor 模式下，组件四角出现黑框。

**根因**：`iconColor` 设于容器 `background`，mask 层的 `mix-blend-mode: screen` 与容器背景混合。`border-radius` 裁剪 mask 后，四角区域露出容器背景色。

**修复**：改为 overlay 独立层架构（见最终架构），颜色由 overlay 自身承载，不与容器背景耦合。

---

## API 参考

### Props

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `icons` | `Array` | `[]` | 图标列表，支持 emoji / SVG path 片段 / 完整 SVG 字符串 |
| `modelValue` | `Number` | `undefined` | v-model 绑定值 |
| `currentIndex` | `Number` | `0` | 兼容非 v-model 场景 |
| `size` | `Number` | `80` | 图标区域宽高 (px) |
| `duration` | `Number` | `600` | 动画总时长 (ms) |
| `maxBlur` | `Number` | `14` | 最大模糊半径 (px)，progress=0.5 时达到峰值 |
| `contrastStrength` | `Number` | `22` | alpha 阈值增强强度（CSS contrast 倍数） |
| `preserveColor` | `Boolean` | `false` | `true`：mask+overlay 保色方案；`false`：灰度方案 |
| `easing` | `String` | `'cubic-bezier(0.34,1.56,0.64,1)'` | 缓动曲线 |
| `backgroundColor` | `String` | `'#ffffff'` | mask 层背景色 |
| `iconColor` | `String` | `'#1a1a2e'` | preserveColor 时的目标颜色 |

### easing 取值

| 关键字 | 效果 |
|--------|------|
| `'cubic-bezier(0.65,0,0.35,1)'` | **自然融合**（推荐） |
| `'cubic-bezier(0.34,1.56,0.64,1)'` | 弹性 Q 弹 |
| `'ease-in-out'` | 对称缓入缓出 |
| `'linear'` | 匀速 |
| 自定义 cubic-bezier | 完全自由 |

### Slots

| 插槽 | 作用域 | 说明 |
|------|--------|------|
| `icon-{N}` | `{ icon, index, isActive }` | 索引 N 的自定义渲染 |
| `icon` | `{ icon, index, isActive }` | 所有图标的 fallback 渲染 |

---

## 工程化集成

```vue
<script setup>
import { ref } from 'vue'
import MetaballIconTransition from '@/components/MetaballIconTransition.vue'

const idx = ref(0)
const icons = [
  '<svg viewBox="0 0 360 360"><path d="..." fill="currentColor"/></svg>',
  '<svg viewBox="0 0 360 360"><path d="..." fill="currentColor"/></svg>',
]
</script>

<template>
  <MetaballIconTransition
    v-model="idx"
    :icons="icons"
    :size="100"
    :duration="650"
    :max-blur="14"
    :contrast-strength="20"
    :preserve-color="true"
    icon-color="#4C5FF0"
    easing="cubic-bezier(0.65,0,0.35,1)"
    background-color="#ffffff"
  />
</template>
```

零第三方依赖，复制 `MetaballIconTransition.vue` 到 `src/components/` 即可。

---

## 参数调优

| 图标尺寸 | 推荐 maxBlur | 推荐 contrastStrength |
|----------|-------------|----------------------|
| 32-48px | 5-7 | 18-22 |
| 64-80px | 8-12 | 20-25 |
| 100-160px | 12-18 | 22-28 |
| 200px+ | 18-28 | 25-35 |

经验法则：`maxBlur ≈ size × 0.10~0.15`，`contrastStrength ≈ 20` 起步。

---

## 浏览器兼容性

| 浏览器 | 最低版本 | 备注 |
|--------|---------|------|
| Chrome | 53+ | 完全支持 |
| Firefox | 35+ | 完全支持 |
| Safari | 9.1+ | 需 `-webkit-` 前缀（Vite autoprefixer 自动处理） |
| Edge | 79+ | 完全支持 |

---

## License

MIT
