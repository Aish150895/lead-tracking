// API base URL - for authenticated endpoints
const API_URL = '/api';
// Direct URL for public endpoints
const DIRECT_URL = '';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const text = await response.text();
  const data = text && JSON.parse(text);
  
  if (!response.ok) {
    const error = (data && data.detail) || response.statusText;
    return Promise.reject(error);
  }
  
  return data;
};

// Get auth token from local storage
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Lead service
export const leadService = {
  // Get all leads with optional filtering
  getAllLeads: async (state = null, page = 1, pageSize = 10, search = null) => {
    let url = `${API_URL}/leads?skip=${(page - 1) * pageSize}&limit=${pageSize}`;
    
    // Add optional filters
    if (state) {
      url += `&state=${state}`;
    }
    
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    
    return handleResponse(response);
  },
  
  // Get lead by ID
  getLead: async (id) => {
    const response = await fetch(`${API_URL}/leads/${id}`, {
      method: 'GET',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    
    return handleResponse(response);
  },
  
  // Submit new lead
  submitLead: async (leadData) => {
    // Use FormData for file uploads
    const formData = new FormData();
    formData.append('first_name', leadData.first_name);
    formData.append('last_name', leadData.last_name);
    formData.append('email', leadData.email);
    
    if (leadData.notes) {
      formData.append('notes', leadData.notes);
    }
    
    // Resume is required
    if (!leadData.resume) {
      return Promise.reject("Resume file is required");
    }
    
    formData.append('resume', leadData.resume);
    
    const response = await fetch(`${API_URL}/leads`, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header when using FormData
    });
    
    return handleResponse(response);
  },
  
  // Update lead state
  updateLead: async (id, updateData) => {
    const response = await fetch(`${API_URL}/leads/${id}`, {
      method: 'PATCH',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });
    
    return handleResponse(response);
  },
  
  // Download resume
  downloadResume: async (id) => {
    const response = await fetch(`${API_URL}/leads/${id}/resume`, {
      method: 'GET',
      headers: {
        ...getAuthHeader()
      }
    });
    
    if (!response.ok) {
      const error = await response.text();
      return Promise.reject(error);
    }
    
    return response.blob();
  }
};

// Authentication service
export const authService = {
  // Login
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
    
    return handleResponse(response);
  },
  
  // Get current user
  getCurrentUser: async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
      method: 'GET',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json'
      }
    });
    
    return handleResponse(response);
  }
};