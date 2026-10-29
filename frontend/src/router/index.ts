import { createRouter, createWebHistory } from 'vue-router'
import GameView from '../views/GameView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: 'bot' } },
    { path: '/bot', name: 'bot', component: GameView, props: { mode: 'bot' } },
    { path: '/practice', name: 'practice', component: GameView, props: { mode: 'practice' } },
  ],
})

export default router
