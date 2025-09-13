# InsightHire API Documentation

## Overview
This document describes the API endpoints for candidate management and real-time analysis data in InsightHire.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require authentication. Include the user token in the request headers:
```
Authorization: Bearer <your-token>
```

---

## 🧑‍💼 Candidate Management APIs

### 1. Create Candidate
**POST** `/candidates`

Create a new candidate profile.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "position": "Software Engineer",
  "phone": "+1234567890",
  "experience_years": 5,
  "skills": ["Python", "JavaScript", "React"],
  "education": "Bachelor in Computer Science",
  "resume_url": "https://example.com/resume.pdf",
  "notes": "Strong technical background"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Candidate created successfully",
  "candidate": {
    "id": "candidate-uuid",
    "candidate_id": "candidate-uuid",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "position": "Software Engineer",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "status": "active"
  }
}
```

### 2. Get All Candidates
**GET** `/candidates`

Retrieve all candidates with optional filtering.

**Query Parameters:**
- `limit` (optional): Number of candidates to return (default: 50)
- `status` (optional): Filter by status ('active', 'inactive')

**Example:**
```
GET /candidates?limit=20&status=active
```

**Response (200 OK):**
```json
{
  "status": "success",
  "candidates": [
    {
      "id": "candidate-uuid",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "position": "Software Engineer",
      "status": "active"
    }
  ],
  "count": 1
}
```

### 3. Get Specific Candidate
**GET** `/candidates/{candidate_id}`

Retrieve a specific candidate by ID.

**Response (200 OK):**
```json
{
  "status": "success",
  "candidate": {
    "id": "candidate-uuid",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "position": "Software Engineer",
    "created_at": "2024-01-01T10:00:00Z",
    "status": "active"
  }
}
```

### 4. Update Candidate
**PUT** `/candidates/{candidate_id}`

Update candidate information.

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+1987654321",
  "notes": "Updated information"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Candidate updated successfully",
  "candidate": {
    "id": "candidate-uuid",
    "name": "John Smith",
    "updated_at": "2024-01-01T11:00:00Z"
  }
}
```

### 5. Delete Candidate
**DELETE** `/candidates/{candidate_id}`

Soft delete a candidate (marks as inactive).

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Candidate deleted successfully"
}
```

---

## 📊 Real-time Analysis APIs

### 1. Get Real-time Analysis Data
**GET** `/sessions/{session_id}/analysis`

Retrieve real-time analysis data for a session.

**Query Parameters:**
- `limit` (optional): Number of analysis points to return (default: 100)

**Response (200 OK):**
```json
{
  "status": "success",
  "session_id": "session-uuid",
  "analysis_data": [
    {
      "key": "analysis-key-1",
      "timestamp": "2024-01-01T10:00:00Z",
      "session_id": "session-uuid",
      "face_stress": {
        "stress_level": "low_stress",
        "confidence": 0.85,
        "emotion": "neutral"
      },
      "hand_gesture": {
        "confidence_level": "high",
        "confidence": 0.92
      },
      "eye_tracking": {
        "confidence_level": "medium",
        "confidence": 0.78
      },
      "voice_analysis": {
        "confidence_level": "high",
        "confidence": 0.88
      },
      "overall_score": 0.86
    }
  ],
  "count": 1
}
```

### 2. Get Latest Analysis
**GET** `/sessions/{session_id}/analysis/latest`

Get the most recent analysis summary for a session.

**Response (200 OK):**
```json
{
  "status": "success",
  "session_id": "session-uuid",
  "latest_analysis": {
    "timestamp": "2024-01-01T10:05:00Z",
    "face_stress": {
      "stress_level": "low_stress",
      "confidence": 0.85
    },
    "hand_gesture": {
      "confidence_level": "high",
      "confidence": 0.92
    },
    "eye_tracking": {
      "confidence_level": "medium",
      "confidence": 0.78
    },
    "voice_analysis": {
      "confidence_level": "high",
      "confidence": 0.88
    },
    "overall_score": 0.86
  }
}
```

---

## 🔧 Test & Debug APIs

### 1. Test Database Connection
**GET** `/test/database`

Test the database connections.

**Response (200 OK):**
```json
{
  "status": "success",
  "firestore": "connected",
  "realtime_database": "connected",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 2. Create Test Candidate
**POST** `/test/candidate`

Create a test candidate with sample data.

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Test candidate created successfully",
  "candidate": {
    "id": "test-candidate-uuid",
    "name": "John Doe",
    "email": "john.doe@example.com"
  }
}
```

---

## 🔄 Real-time Data Flow

### Firebase Realtime Database Structure
```
/sessions/
  /{session_id}/
    /analysis/
      /{timestamp-key}/
        - timestamp
        - session_id
        - face_stress: {}
        - hand_gesture: {}
        - eye_tracking: {}
        - voice_analysis: {}
        - overall_score
    /latest_analysis/
      - timestamp
      - face_stress: {}
      - hand_gesture: {}
      - eye_tracking: {}
      - voice_analysis: {}
      - overall_score
```

### WebSocket Events
The system also provides real-time updates via WebSocket:

**Connect to session:**
```javascript
socket.emit('join_session', { session_id: 'your-session-id' });
```

**Receive live updates:**
```javascript
socket.on('live_results', (data) => {
  console.log('Real-time analysis:', data);
});
```

---

## 📝 Error Responses

All endpoints follow a consistent error response format:

```json
{
  "status": "error",
  "message": "Error description"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## 🚀 Usage Examples

### Creating and Managing Candidates

```javascript
// Create a candidate
const candidate = await fetch('/api/candidates', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-token'
  },
  body: JSON.stringify({
    name: 'Jane Smith',
    email: 'jane@example.com',
    position: 'Frontend Developer'
  })
});

// Get all candidates
const candidates = await fetch('/api/candidates');
const data = await candidates.json();
console.log(data.candidates);
```

### Monitoring Real-time Analysis

```javascript
// Get latest analysis
const analysis = await fetch(`/api/sessions/${sessionId}/analysis/latest`);
const data = await analysis.json();
console.log('Latest analysis:', data.latest_analysis);

// Get historical analysis data
const history = await fetch(`/api/sessions/${sessionId}/analysis?limit=50`);
const historyData = await history.json();
console.log('Analysis history:', historyData.analysis_data);
```

---

## 🔐 Security Notes

1. Always validate input data on the client side
2. Use HTTPS in production
3. Implement proper authentication and authorization
4. Sanitize all user inputs
5. Monitor API usage and implement rate limiting

---

## 📞 Support

For questions about the API, please check the logs or contact the development team.
