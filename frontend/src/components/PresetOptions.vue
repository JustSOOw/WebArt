<template>
  <div class="preset-options">
    <div class="style-grid">
      <div 
        v-for="style in presetStyles" 
        :key="style.value"
        class="style-card"
        :class="{ active: selectedStyle === style.value, disabled: loading }"
        @click="selectStyle(style.value)"
      >
        <div class="style-image">
          <img :src="style.imageUrl" :alt="style.label" />
        </div>
        <div class="style-name">{{ style.label }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'PresetOptions',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['style-selected'],
  setup(props, { emit }) {
    const selectedStyle = ref('')
    
    const presetStyles = [
      {
        label: '奇幻楼阁',
        value: 'fantasy_pavilion',
        imageUrl: '/styles/fantasy_pavilion.jpg'
      },
      {
        label: '绝色佳人',
        value: 'peerless_beauty',
        imageUrl: '/styles/peerless_beauty.jpg'
      },
      {
        label: '山水楼阁',
        value: 'landscape_pavilion',
        imageUrl: '/styles/landscape_pavilion.jpg'
      },
      {
        label: '古风建筑',
        value: 'traditional_buildings',
        imageUrl: '/styles/traditional_buildings.jpg'
      },
      {
        label: '青龙女侠',
        value: 'green_dragon_girl',
        imageUrl: '/styles/green_dragon_girl.jpg'
      },
      {
        label: '樱花烂漫',
        value: 'cherry_blossoms',
        imageUrl: '/styles/cherry_blossoms.jpg'
      },
      {
        label: '可爱少女',
        value: 'lovely_girl',
        imageUrl: '/styles/lovely_girl.jpg'
      },
      {
        label: '水墨少侠',
        value: 'ink_hero',
        imageUrl: '/styles/ink_hero.jpg'
      },
      {
        label: '动漫少女',
        value: 'anime_girl',
        imageUrl: '/styles/anime_girl.jpg'
      },
      {
        label: '水中楼阁',
        value: 'lake_pavilion',
        imageUrl: '/styles/lake_pavilion.jpg'
      },
      {
        label: '宁静乡村',
        value: 'tranquil_countryside',
        imageUrl: '/styles/tranquil_countryside.jpg'
      },
      {
        label: '黄昏美景',
        value: 'dusk_splendor',
        imageUrl: '/styles/dusk_splendor.jpg'
      }
    ]
    
    const selectStyle = (style) => {
      if (props.loading) return
      selectedStyle.value = style
      emit('style-selected', style)
    }
    
    return {
      selectedStyle,
      presetStyles,
      selectStyle
    }
  }
}
</script>

<style scoped>
.preset-options {
  padding: 16px 0;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.style-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background-color: #fff;
}

.style-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.style-card.active {
  border: 2px solid var(--primary-color);
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.style-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.style-image {
  width: 100%;
  height: 100px;
  overflow: hidden;
}

.style-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.style-card:hover .style-image img {
  transform: scale(1.05);
}

.style-name {
  padding: 8px;
  text-align: center;
  font-size: 14px;
  color: var(--text-color);
  background-color: rgba(255, 255, 255, 0.9);
}

@media (max-width: 768px) {
  .style-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .style-grid {
    grid-template-columns: 1fr;
  }
}
</style> 