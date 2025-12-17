import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/HomeView.vue'
import LogoutView from '../views/LogoutView.vue'
import RegisterView from '../views/RegisterView.vue'
import CreaContoView from '../views/CreaContoView.vue'
import DashboardView from '../views/DashboardView.vue'

import { useAuth } from '@/stores/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: {
        requiresAuth:true
      }
    },
    {
      path: '/logout',
      name: 'logout',
      component: () => import('../views/LogoutView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/crea_conto',
      name: 'crea_conto',
      component: () => import('../views/CreaContoView.vue'),
      meta: {
          requiresAuth:true
        }
    },
    {
      path: '/nuovo_deposito',
      name: 'nuovo_deposito',
      component: () => import('../views/NuovoDepositoView.vue'),
      meta: {
          requiresAuth:true
        }
    },
    {
      path: '/nuovo_bonifico',
      name: 'nuovo_bonifico',
      component: () => import('../views/NuovoBonificoView.vue'),
      meta: {
          requiresAuth:true
        }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  const requiresAuth = to.meta?.requiresAuth
  const isAuthenticated = !!auth.token

  if (requiresAuth && !isAuthenticated) {
    console.log("Accesso negato. Riprova.")
    next({name: 'login' })
  } else {
      next()
    }
})

export default router
