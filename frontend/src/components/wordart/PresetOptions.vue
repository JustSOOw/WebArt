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
// 导入所有图片
import fantasyPavilion from '../../assets/images/fantasy_pavilion.png'
import peerlessBeauty from '../../assets/images/peerless_beauty.png'
import landscapePavilion from '../../assets/images/landscape_pavilion.png'
import traditionalBuildings from '../../assets/images/traditional_buildings.png'
import greenDragonGirl from '../../assets/images/green_dragon_girl.webp'
import cherryBlossoms from '../../assets/images/cherry_blossoms.png'
import lovelyGirl from '../../assets/images/lovely_girl.png'
import inkHero from '../../assets/images/ink_hero.png'
import animeGirl from '../../assets/images/anime_girl.png'
import lakePavilion from '../../assets/images/lake_pavilion.png'
import tranquilCountryside from '../../assets/images/tranquil_countryside.png'
import duskSplendor from '../../assets/images/dusk_splendor.png'

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
        imageUrl: fantasyPavilion
      },
      {
        label: '绝色佳人',
        value: 'peerless_beauty',
        imageUrl: peerlessBeauty
      },
      {
        label: '山水楼阁',
        value: 'landscape_pavilion',
        imageUrl: landscapePavilion
      },
      {
        label: '古风建筑',
        value: 'traditional_buildings',
        imageUrl: traditionalBuildings
      },
      {
        label: '青龙女侠',
        value: 'green_dragon_girl',
        imageUrl: greenDragonGirl
      },
      {
        label: '樱花烂漫',
        value: 'cherry_blossoms',
        imageUrl: cherryBlossoms
      },
      {
        label: '可爱少女',
        value: 'lovely_girl',
        imageUrl: lovelyGirl
      },
      {
        label: '水墨少侠',
        value: 'ink_hero',
        imageUrl: inkHero
      },
      {
        label: '动漫少女',
        value: 'anime_girl',
        imageUrl: animeGirl
      },
      {
        label: '水中楼阁',
        value: 'lake_pavilion',
        imageUrl: lakePavilion
      },
      {
        label: '宁静乡村',
        value: 'tranquil_countryside',
        imageUrl: tranquilCountryside
      },
      {
        label: '黄昏美景',
        value: 'dusk_splendor',
        imageUrl: duskSplendor
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