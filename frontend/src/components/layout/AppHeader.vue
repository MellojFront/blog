<script setup lang="ts">
import { Button } from '@/components/ui/button'
import ModeToggle from '@/components/ui/ModeToggle.vue'
</script>

<template>

  <header class="sticky top-0 z-50 w-full border-b backdrop-blur">
    <div class="container mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
      
      <!-- Левая часть: Логотип и навигация -->
      <div class="flex items-center gap-6">
        <a href="/" class="text-lg font-bold tracking-tight">
          Blog
        </a>
        
        <nav class="hidden md:flex items-center gap-6 text-sm font-medium">
          <a href="/post" class="text-muted-foreground transition-colors hover:text-foreground">
            Post
          </a>
          <a href="/about" class="text-muted-foreground transition-colors hover:text-foreground">
            About
          </a>
        </nav>
      </div>

      <!-- Правая часть: Действия и переключатель темы -->
      <div class="flex items-center gap-2">
        <Button variant="ghost" size="sm" as-child>
          <a href="/login">Sign in</a>
        </Button>
        <ModeToggle />
      </div>

    </div>
  </header>
</template>
