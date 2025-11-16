import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class ChromaDBAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  async query(message, nResults = 5) {
    try {
      const response = await this.client.post('/query', {
        query: message,
        n_results: nResults
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      if (error.code === 'ECONNREFUSED') {
        return {
          success: false,
          error: 'Cannot connect to GHL WHIZ backend. Make sure the server is running on http://localhost:8000'
        };
      }
      return {
        success: false,
        error: error.message || 'An error occurred while querying the database'
      };
    }
  }

  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

export default new ChromaDBAPI();
