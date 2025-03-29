import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/wordart'
  },
  {
    path: '/wordart',
    name: 'WordArt',
    component: () => import('../views/WordArtView.vue'),
    meta: {
      title: '百家姓生成'
    }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatView.vue'),
    meta: {
      title: 'AI对话'
    }
  },
  // 未来的路由会添加在这里
  // {
  //   path: '/video',
  //   name: 'Video',
  //   component: () => import('../views/VideoView.vue'),
  //   meta: {
  //     title: 'AI视频生成'
  //   }
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由标题更新
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - WordArt锦书` : 'WordArt锦书'
  next()
})

export default router 