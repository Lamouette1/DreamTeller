<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Load Saved Stories</h1>
    <load-story />
  </div>
</template>

<script>
import LoadStory from '@/components/LoadStory.vue'

export default {
  name: 'LoadStoryView',
  components: {
    LoadStory
  }
}
</script>