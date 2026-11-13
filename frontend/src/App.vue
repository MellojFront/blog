<script setup lang="ts">
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { Card } from '@/components/ui/card'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
</script>

<template>
  <SidebarProvider>
    <!-- 1. Левая колонка: само боковое меню -->
    <AppSidebar />

    <!-- 2. Правая колонка: шапка + основной контент -->
    <SidebarInset>
      <!-- Полоска сверху с кнопкой сворачивания и твоей шапкой -->
      <div class="flex items-center border-b px-4">
        <SidebarTrigger class="mr-2" />
        <div class="flex-1">
          <AppHeader />
        </div>
      </div>

      <!-- Твой контент и карточки -->
      <main class="flex-1 container mx-auto max-w-5xl px-4 py-8">
        <h1 class="text-3xl font-bold mb-4">Hello it's my blog and pet project</h1>
        
        <div class="mb-6 space-y-1">
          <p class="text-xs font-medium">Project stack</p>
          <p class="text-xs font-light">Python:</p>
          <p class="text-xs font-light">- FastAPI</p>
          <p class="text-xs font-light">- PostgreSQL</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card class="p-6">Статья 1</Card>
          <Card class="p-6">Статья 2</Card>
          <Card class="p-6">Статья 3</Card>
        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
