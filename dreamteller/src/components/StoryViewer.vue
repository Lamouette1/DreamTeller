// src/components/StoryViewer.vue
<template>
  <div>
    <div v-if="story" class="space-y-8">
      <!-- Story Header -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">{{ story.title }}</h1>
        <p class="text-gray-600 dark:text-gray-400">{{ storyDetails }}</p>

        <!-- Export Options -->
        <div class="mt-4 flex space-x-3">
         <button 
            @click="saveStory" 
            class="inline-flex items-center px-4 py-2 border border-green-300 shadow-sm text-sm font-medium rounded-md text-green-700 dark:text-green-300 bg-white dark:bg-gray-700 hover:bg-green-50 dark:hover:bg-green-900/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="saving"
            >
            <svg v-if="!saving" class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
            </svg>
            <svg v-else class="mr-2 h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ saving ? 'Saving...' : 'Save Story' }}
          </button>
          <button 
            @click="exportToPDF" 
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="pdfLoading"
          >
            <svg v-if="!pdfLoading" class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
            </svg>
            <svg v-else class="mr-2 h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ pdfLoading ? 'Generating...' : 'Export as PDF' }}
          </button>
        </div>

        <!-- Success Message -->
        <div v-if="successMessage" class="mt-4 bg-green-50 dark:bg-green-900/20 p-3 rounded-md">
          <p class="text-sm text-green-800 dark:text-green-300">{{ successMessage }}</p>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="mt-4 bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
          <p class="text-sm text-red-800 dark:text-red-300">{{ errorMessage }}</p>
        </div>
      </div>

      <!-- Scene Cards -->
      <div class="grid grid-cols-1 gap-6">
        <scene-card
          v-for="(scene, index) in story.scenes"
          :key="index"
          :scene="scene"
          :scene-index="index"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="flex justify-center items-center h-64">
      <div class="loader flex items-center">
        <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="ml-3 text-lg text-gray-600 dark:text-gray-400">Loading your story...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="bg-white dark:bg-gray-800 shadow rounded-lg p-6 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900 dark:text-white">Story not found</h3>
      <p class="mt-1 text-gray-500 dark:text-gray-400">The story you're looking for doesn't exist or is still being generated.</p>
      <div class="mt-6">
        <router-link to="/create" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Create a New Story
        </router-link>
      </div>
    </div>

    <!-- PDF Loading Overlay -->
    <div v-if="pdfLoading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg text-center max-w-md">
        <svg class="animate-spin h-12 w-12 text-indigo-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-white">Generating PDF</h3>
        <p class="mt-2 text-gray-500 dark:text-gray-400">Please wait while we prepare your story for download...</p>
        <p class="mt-1 text-sm text-gray-400 dark:text-gray-500">This may take a moment, especially for stories with multiple images.</p>
      </div>
    </div>
  </div>
</template>

<script>
import SceneCard from '@/components/SceneCard.vue'
import html2pdf from 'html2pdf.js'
import storyService from '@/services/storyService'

export default {
  name: 'StoryViewer',
  components: {
    SceneCard
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: false,
      pdfLoading: false,
      saving: false,
      shareUrl: '',
      showShareMessage: false,
      successMessage: '',
      errorMessage: ''
    }
  },
  computed: {
    story() {
      return this.$store.getters.getStoryById(this.id) || this.$store.state.currentStory
    },
    storyDetails() {
      if (!this.story) return ''
      return `A ${this.story.prompt.genre.toLowerCase()} story with a ${this.story.prompt.tone.toLowerCase()} tone, illustrated in ${this.story.prompt.artStyle.toLowerCase()} style.`
    }
  },
  created() {
    this.loading = true
    // If story is not in the store, we could fetch it from an API
    // For now, we'll just set loading to false after a short delay
    setTimeout(() => {
      this.loading = false
    }, 1000)
  },
  methods: {
    async saveStory() {
      if (!this.story) {
        this.errorMessage = 'Cannot save: story not found';
        return;
      }

      this.saving = true;
      this.errorMessage = '';
      this.successMessage = '';

      try {
        // Generate a filename based on the story title
        const defaultFilename = this.story.title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '_')
          .replace(/^_+|_+$/g, '');

        console.log('Saving story with ID:', this.story.id);
        console.log('Generated filename:', defaultFilename);

        // Call the API to save the story
        const result = await storyService.saveStory(this.story.id, defaultFilename);

        this.successMessage = `Story saved successfully as "${result.filename}"`;
        console.log('Story saved:', result);

        // Clear success message after 5 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 5000);

      } catch (error) {
        console.error('Failed to save story:', error);
        this.errorMessage = error.response?.data?.detail || 'Failed to save story. Please try again.';
        
        // Clear error message after 8 seconds
        setTimeout(() => {
          this.errorMessage = '';
        }, 8000);
      } finally {
        this.saving = false;
      }
    },

    exportToPDF() {
      if (!this.story) {
        this.errorMessage = 'Cannot export: story not found';
        return;
      }

      this.pdfLoading = true;
      this.errorMessage = '';
      this.successMessage = '';

      // Create a container for the PDF content
      const container = document.createElement('div');
      container.style.padding = '20px';
      container.style.fontFamily = 'Arial, sans-serif';

      // Add the story title and details
      const header = document.createElement('div');
      header.innerHTML = `
        <h1 style="font-size: 28px; margin-bottom: 10px; color: #333; text-align: center;">${this.story.title}</h1>
        <p style="font-size: 14px; color: #666; margin-bottom: 30px; text-align: center;">${this.storyDetails}</p>
      `;
      container.appendChild(header);

      // Track image loading with promises
      const imagePromises = [];

      // Add each scene to the container
      this.story.scenes.forEach((scene, index) => {
        const sceneDiv = document.createElement('div');
        sceneDiv.style.marginBottom = '40px';
        sceneDiv.style.pageBreakInside = 'avoid'; // Try to keep scenes on the same page

        // Scene header
        const sceneHeader = document.createElement('h2');
        sceneHeader.textContent = `Scene ${index + 1}`;
        sceneHeader.style.fontSize = '22px';
        sceneHeader.style.marginBottom = '15px';
        sceneHeader.style.borderBottom = '1px solid #ddd';
        sceneHeader.style.paddingBottom = '8px';
        sceneHeader.style.color = '#444';
        sceneDiv.appendChild(sceneHeader);

        // Scene image (if available)
        if (scene.imageUrl) {
          const imagePromise = new Promise((resolve) => {
            const img = new Image();
            img.crossOrigin = 'Anonymous'; // Enable cross-origin loading

            img.onload = () => {
              // Create image container
              const imgContainer = document.createElement('div');
              imgContainer.style.textAlign = 'center';
              imgContainer.style.marginBottom = '20px';

              // Style the image
              img.style.maxWidth = '500px';
              img.style.maxHeight = '400px';
              img.style.objectFit = 'contain';
              img.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
              img.style.borderRadius = '8px';

              imgContainer.appendChild(img);
              sceneDiv.appendChild(imgContainer);
              resolve();
            };

            img.onerror = () => {
              // Create placeholder for failed image
              const placeholder = document.createElement('div');
              placeholder.style.width = '100%';
              placeholder.style.height = '200px';
              placeholder.style.backgroundColor = '#f1f1f1';
              placeholder.style.display = 'flex';
              placeholder.style.alignItems = 'center';
              placeholder.style.justifyContent = 'center';
              placeholder.style.marginBottom = '20px';
              placeholder.style.borderRadius = '8px';
              placeholder.textContent = 'Image could not be loaded';
              placeholder.style.color = '#888';

              sceneDiv.appendChild(placeholder);
              resolve(); // Still resolve the promise to continue PDF generation
            };

            img.src = scene.imageUrl;
          });

          imagePromises.push(imagePromise);
        }

        // Scene text
        const textDiv = document.createElement('div');
        textDiv.style.lineHeight = '1.6';
        textDiv.style.fontSize = '14px';
        textDiv.style.color = '#333';
        textDiv.style.textAlign = 'justify';

        // Split the text into paragraphs for better formatting
        const paragraphs = scene.text.split('\n').filter(p => p.trim());
        if (paragraphs.length === 0) {
          // If no paragraphs, just use the entire text
          textDiv.innerHTML = `<p>${scene.text}</p>`;
        } else {
          // Add each paragraph
          textDiv.innerHTML = paragraphs.map(p => `<p style="margin-bottom: 10px;">${p}</p>`).join('');
        }

        sceneDiv.appendChild(textDiv);
        container.appendChild(sceneDiv);
      });

      // Wait for all images to load before generating PDF
      Promise.all(imagePromises)
        .then(() => {
          // Configure PDF options
          const opt = {
            margin: [0.75, 0.75, 0.75, 0.75], // Margins in inches [top, right, bottom, left]
            filename: `${this.story.title.replace(/\s+/g, '_')}.pdf`,
            image: { 
              type: 'jpeg', 
              quality: 0.98 // Higher quality for images
            },
            html2canvas: { 
              scale: 2, // Higher scale for better image quality
              useCORS: true, // Enable CORS for images
              allowTaint: true, // Allow tainted canvas
              logging: true, // Enable logging for debugging
              letterRendering: true // Improve text rendering
            },
            jsPDF: { 
              unit: 'in', 
              format: 'letter', 
              orientation: 'portrait',
              compress: true,
              hotfixes: ["px_scaling"] // Fix for image scaling issues
            },
            pagebreak: { 
              mode: ['avoid-all', 'css', 'legacy'],
              before: '.page-break-before',
              after: '.page-break-after',
              avoid: '.page-break-avoid'
            }
          };

          // Generate the PDF
          html2pdf()
            .from(container)
            .set(opt)
            .save()
            .then(() => {
              this.pdfLoading = false;
              this.successMessage = 'PDF generated successfully!';

              // Clear success message after 5 seconds
              setTimeout(() => {
                this.successMessage = '';
              }, 5000);
            })
            .catch(error => {
              console.error('PDF generation error:', error);
              this.pdfLoading = false;
              this.errorMessage = 'Failed to generate PDF. Please try again.';
            });
        })
        .catch(error => {
          console.error('Image loading error:', error);
          this.pdfLoading = false;
          this.errorMessage = 'Error loading images for PDF generation.';
        });
    },

    copyShareLink() {
      // In a real app, this would create a unique URL for sharing
      const shareableUrl = `${window.location.origin}/story/${this.id}`
      navigator.clipboard.writeText(shareableUrl)
        .then(() => {
          this.shareUrl = shareableUrl
          this.showShareMessage = true
          this.successMessage = 'Share link copied to clipboard!';
          setTimeout(() => {
            this.showShareMessage = false
            this.successMessage = '';
          }, 3000)
        })
        .catch(err => {
          console.error('Failed to copy URL: ', err)
          this.errorMessage = 'Failed to copy share link.';
        })
    }
  }
}
</script>

<style scoped>
/* Add any component-specific styles here */
.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>