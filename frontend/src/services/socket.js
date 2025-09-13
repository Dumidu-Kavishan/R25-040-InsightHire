import { io } from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect() {
    if (!this.socket) {
      const serverUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';
      
      this.socket = io(serverUrl, {
        transports: ['websocket', 'polling'],
        autoConnect: true,
      });

      this.socket.on('connect', () => {
        this.isConnected = true;
        console.log('Connected to server');
      });

      this.socket.on('disconnect', () => {
        this.isConnected = false;
        console.log('Disconnected from server');
      });

      this.socket.on('connected', (data) => {
        console.log('Server message:', data.message);
      });

      // Listen for real-time analysis updates
      this.socket.on('analysis_update', (data) => {
        console.log('📊 Analysis Update Received:', data);
        // Emit a custom event that components can listen to
        window.dispatchEvent(new CustomEvent('analysisUpdate', { detail: data }));
      });

      // Listen for session join confirmation
      this.socket.on('joined_session', (data) => {
        console.log('🔌 Joined Session:', data);
        if (data.analysis_active) {
          console.log('✅ Analysis is active for this session');
        } else {
          console.warn('⚠️ Analysis is not active - start interview first');
        }
        // Emit a custom event for session join status
        window.dispatchEvent(new CustomEvent('sessionJoined', { detail: data }));
      });
    }

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Session methods
  joinSession(sessionId) {
    if (this.socket) {
      this.socket.emit('join_session', { session_id: sessionId });
    }
  }

  leaveSession(sessionId) {
    if (this.socket) {
      this.socket.emit('leave_session', { session_id: sessionId });
    }
  }

  // Real-time data methods
  sendVideoFrame(sessionId, frameData) {
    if (this.socket && this.isConnected) {
      if (frameData) {
        console.log('📡 SOCKET: Sending video frame', {
          sessionId,
          frameDataLength: frameData.length,
          isConnected: this.isConnected,
          socketId: this.socket.id
        });
      } else {
        console.log('🛑 SOCKET: Sending video stop signal', {
          sessionId,
          isConnected: this.isConnected,
          socketId: this.socket.id
        });
      }
      
      this.socket.emit('video_frame', {
        session_id: sessionId,
        frame: frameData
      });
    } else {
      console.error('❌ SOCKET: Cannot send frame - not connected', {
        hasSocket: !!this.socket,
        isConnected: this.isConnected
      });
    }
  }

  sendAudioData(sessionId, audioData, sampleRate = 22050) {
    if (this.socket && this.isConnected) {
      console.log('🎤 SOCKET: Sending audio data', {
        sessionId,
        audioDataLength: audioData ? audioData.length : 0,
        sampleRate,
        isNull: audioData === null,
        isConnected: this.isConnected,
        socketId: this.socket.id
      });
      
      this.socket.emit('audio_data', {
        session_id: sessionId,
        audio: audioData,
        sample_rate: sampleRate,
        is_stop_signal: audioData === null
      });
    } else {
      console.warn('🎤 SOCKET: Cannot send audio - not connected', {
        hasSocket: !!this.socket,
        isConnected: this.isConnected
      });
    }
  }

  requestLiveResults(sessionId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('get_live_results', { session_id: sessionId });
    }
  }

  // Event listeners
  onLiveResults(callback) {
    if (this.socket) {
      this.socket.on('live_results', callback);
    }
  }

  onJoinedSession(callback) {
    if (this.socket) {
      this.socket.on('joined_session', callback);
    }
  }

  // Remove event listeners
  offLiveResults() {
    if (this.socket) {
      this.socket.off('live_results');
    }
  }

  offJoinedSession() {
    if (this.socket) {
      this.socket.off('joined_session');
    }
  }

  // Get connection status
  getConnectionStatus() {
    return this.isConnected;
  }
}

// Create singleton instance
const socketService = new SocketService();

export default socketService;
