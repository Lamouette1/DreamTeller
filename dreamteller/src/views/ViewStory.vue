<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <story-viewer :id="id" />
  </div>
</template>

<script>
import StoryViewer from '@/components/StoryViewer.vue'

export default {
  name: 'ViewStory',
  components: {
    StoryViewer
  },
  props: {
    id: {
      type: String,
      required: true
    }
  }
}
</script>
