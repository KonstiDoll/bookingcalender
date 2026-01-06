<script setup lang="ts">
import { parties } from '../composables/useApi'
</script>

<template>
  <div class="flex flex-wrap gap-2 justify-center mb-8">
    <div
      v-for="party in parties"
      :key="party.id"
      class="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-black/5 shadow-sm"
    >
      <span
        class="w-3 h-3 rounded-full shrink-0"
        :style="{ backgroundColor: party.color }"
      />
      <span class="text-sm font-medium text-text-primary whitespace-nowrap">
        {{ party.name }}
      </span>
    </div>
  </div>
</template>
