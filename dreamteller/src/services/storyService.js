// src/services/storyService.js
import axios from 'axios'

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000'

export default {
  async generateStory(storyPrompt) {
    try {
      const response = await axios.post(`${API_URL}/api/stories/generate`, storyPrompt)
      return response.data
    } catch (error) {
      console.error('Error generating story:', error)
      throw error
    }
  },
  
  async regenerateSceneText(prompt, currentText, sceneIndex) {
    try {
      const response = await axios.post(`${API_URL}/api/stories/regenerate-text`, {
        prompt,
        currentText,
        sceneIndex
      })
      return response.data.text
    } catch (error) {
      console.error('Error regenerating scene text:', error)
      throw error
    }
  },
  
  async getStories() {
    try {
      const response = await axios.get(`${API_URL}/api/stories`)
      return response.data
    } catch (error) {
      console.error('Error fetching stories:', error)
      throw error
    }
  },
  
  async getStory(id) {
    try {
      const response = await axios.get(`${API_URL}/api/stories/${id}`)
      return response.data
    } catch (error) {
      console.error('Error fetching story:', error)
      throw error
    }
  },
  
  // New save/load functionality
  async saveStory(storyId, filename = null) {
    try {
      const params = filename ? { filename } : {}
      const response = await axios.post(`${API_URL}/api/stories/${storyId}/save`, null, { params })
      return response.data
    } catch (error) {
      console.error('Error saving story:', error)
      throw error
    }
  },
  
  async listSavedStories() {
    try {
      const response = await axios.get(`${API_URL}/api/stories/saved/list`)
      return response.data
    } catch (error) {
      console.error('Error listing saved stories:', error)
      throw error
    }
  },
  
  async loadSavedStory(filename) {
    try {
      const response = await axios.post(`${API_URL}/api/stories/saved/load/${filename}`)
      return response.data
    } catch (error) {
      console.error('Error loading story:', error)
      throw error
    }
  },
  
  async downloadStory(filename) {
    try {
      const response = await axios.get(`${API_URL}/api/stories/saved/download/${filename}`, {
        responseType: 'blob'
      })
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename.endsWith('.story') ? filename : `${filename}.story`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Error downloading story:', error)
      throw error
    }
  },
  
  async deleteSavedStory(filename) {
    try {
      const response = await axios.delete(`${API_URL}/api/stories/saved/${filename}`)
      return response.data
    } catch (error) {
      console.error('Error deleting story:', error)
      throw error
    }
  },
  
  async uploadStory(file) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_URL}/api/stories/saved/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error uploading story:', error)
      throw error
    }
  }
}