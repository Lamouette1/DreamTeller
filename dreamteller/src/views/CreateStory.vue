<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Create Your Story</h1>
    <story-input />
  </div>
</template>

<script>
import StoryInput from '@/components/StoryInput.vue'

export default {
  name: 'CreateStory',
  components: {
    StoryInput
  }
}
</script>
