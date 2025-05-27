<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">About DreamTeller</h1>

      <div class="space-y-6 text-gray-700 dark:text-gray-300">
        <p class="text-base leading-relaxed">
          DreamTeller is a collaborative AI-powered tool designed to generate short illustrated stories from user prompts. It leverages the OpenAI language model for story generation and diffusion models for dynamic scene illustration. The application simulates a full creative pipeline—from user idea to fully illustrated digital storytelling.
        </p>

        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">The Team</h2>
          <ul class="list-disc pl-6 space-y-2">
            <li>Charles Fassel-Ashley – TEK4 – Project Designer & Developer</li>
            <li>Thomas Fiancette – TEK4 – Project Designer & Developer</li>
            <li>Eliyan Dochev – TEK4 – Project Designer & Developer</li>
          </ul>
        </div>

        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">How It Works</h2>
          <p class="mb-3 text-base leading-relaxed">
            When you submit a story idea, DreamTeller uses advanced AI to:
          </p>
          <ol class="list-decimal pl-6 space-y-2">
            <li>Analyze your prompt and generate a cohesive narrative in your chosen genre and tone</li>
            <li>Break the story into logical scenes for illustration</li>
            <li>Create unique illustrations for each scene using diffusion models</li>
            <li>Present you with a complete story that you can edit, regenerate, and share</li>
          </ol>
        </div>

        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">Technology</h2>
          <p class="mb-3 text-base leading-relaxed">
            DreamTeller is built using:
          </p>
          <ul class="list-disc pl-6 space-y-2">
            <li>Frontend: Vue.js with TailwindCSS</li>
            <li>Backend: Python with FastAPI</li>
            <li>AI: OpenAI GPT API for text, Replicate/Stability Diffusion API for images</li>
            <li>Hosting: Netlify</li>
          </ul>
        </div>

        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mt-8 mb-4">Privacy & Data</h2>
          <p class="text-base leading-relaxed">
            We value your privacy. Your story ideas and generated content are yours to keep and share as you wish. We don't claim ownership of any generated content, though we may store stories for system improvement purposes.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script>