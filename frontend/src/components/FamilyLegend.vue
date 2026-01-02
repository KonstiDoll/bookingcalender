<script setup>
import { parties } from '../composables/useApi'

const props = defineProps({
  selectedParty: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select'])

function selectParty(id) {
  emit('select', props.selectedParty === id ? null : id)
}
</script>

<template>
  <div class="flex flex-wrap gap-2 justify-center mb-8">
    <button
      v-for="party in parties"
      :key="party.id"
      class="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-black/5 cursor-pointer transition-all duration-200 shadow-sm hover:-translate-y-0.5 hover:shadow-md"
      :class="{ 'ring-2 ring-offset-2': selectedParty === party.id }"
      :style="{
        '--tw-ring-color': party.color,
        borderColor: selectedParty === party.id ? party.color : undefined
      }"
      @click="selectParty(party.id)"
    >
      <span
        class="w-3 h-3 rounded-full shrink-0"
        :style="{ backgroundColor: party.color }"
      />
      <span class="text-sm font-medium text-text-primary whitespace-nowrap">
        {{ party.name }}
      </span>
    </button>
  </div>
</template>
