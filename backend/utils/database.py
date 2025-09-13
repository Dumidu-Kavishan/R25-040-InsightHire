"""
Database Manager for InsightHire
"""
from firebase_config import db, rtdb
from firebase_admin import db as firebase_rtdb
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, user_id=None):
        self.db = db
        self.rtdb = rtdb  # This should be the firebase_admin.db module
        self.user_id = user_id
        
        # Log initialization for debugging
        logger.debug(f"DatabaseManager initialized - db: {type(self.db)}, rtdb: {type(self.rtdb)}")
    
    def _get_rtdb_reference(self, path):
        """Get a proper Realtime Database reference"""
        try:
            # Use the firebase_admin.db module directly to ensure proper auth
            return firebase_rtdb.reference(path)
        except Exception as e:
            logger.error(f"❌ Error creating rtdb reference for path '{path}': {e}")
            return None
    
    # ==================== USER PROFILE MANAGEMENT ====================
    
    def create_user_profile(self, profile_data):
        """Create a new user profile"""
        try:
            user_id = profile_data.get('user_id') or profile_data.get('uid')
            if not user_id:
                logger.error("User ID is required for profile creation")
                return None
            
            profile_data.update({
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            profile_ref = self.db.collection('user_profiles').document(user_id)
            profile_ref.set(profile_data)
            logger.info(f"User profile created for user: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            return None
    
    def get_user_profile(self, user_id):
        """Get user profile by user ID"""
        try:
            profile_ref = self.db.collection('user_profiles').document(user_id)
            profile_doc = profile_ref.get()
            
            if profile_doc.exists:
                profile_data = profile_doc.to_dict()
                logger.info(f"User profile retrieved for user: {user_id}")
                return profile_data
            else:
                logger.info(f"No profile found for user: {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, user_id, update_data):
        """Update user profile"""
        try:
            update_data.update({
                'updated_at': datetime.now().isoformat()
            })
            
            profile_ref = self.db.collection('user_profiles').document(user_id)
            # Use set with merge=True to create if doesn't exist, update if exists
            profile_ref.set(update_data, merge=True)
            logger.info(f"User profile updated for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
    
    def delete_user_profile(self, user_id):
        """Delete user profile"""
        try:
            profile_ref = self.db.collection('user_profiles').document(user_id)
            profile_ref.delete()
            logger.info(f"User profile deleted for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user profile: {e}")
            return False

    # ==================== CANDIDATE MANAGEMENT ====================
    
    def create_candidate(self, candidate_data):
        """Create a new candidate profile"""
        try:
            candidate_id = str(uuid.uuid4())
            candidate_data.update({
                'candidate_id': candidate_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'active'
            })
            
            candidate_ref = self.db.collection('candidates').document(candidate_id)
            candidate_ref.set(candidate_data)
            logger.info(f"Candidate created with ID: {candidate_id}")
            return candidate_id
        except Exception as e:
            logger.error(f"Error creating candidate: {e}")
            return None
    
    def get_candidate(self, candidate_id):
        """Get candidate profile by ID"""
        try:
            candidate_ref = self.db.collection('candidates').document(candidate_id)
            doc = candidate_ref.get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting candidate: {e}")
            return None
    
    def get_all_candidates(self, limit=50, status=None):
        """Get all candidates with optional filtering"""
        try:
            query = self.db.collection('candidates')
            
            if status:
                query = query.where('status', '==', status)
            
            query = query.order_by('created_at', direction='DESCENDING').limit(limit)
            docs = query.stream()
            
            candidates = []
            for doc in docs:
                candidates.append({'id': doc.id, **doc.to_dict()})
            
            return candidates
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return []
    
    def update_candidate(self, candidate_id, update_data):
        """Update candidate profile"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            candidate_ref = self.db.collection('candidates').document(candidate_id)
            candidate_ref.update(update_data)
            logger.info(f"Candidate updated: {candidate_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating candidate: {e}")
            return False
    
    def delete_candidate(self, candidate_id):
        """Soft delete candidate (mark as inactive)"""
        try:
            candidate_ref = self.db.collection('candidates').document(candidate_id)
            candidate_ref.update({
                'status': 'inactive',
                'updated_at': datetime.now().isoformat()
            })
            logger.info(f"Candidate deleted: {candidate_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting candidate: {e}")
            return False
    
    # ==================== INTERVIEW SESSION MANAGEMENT ====================
    
    def create_interview_session(self, session_data):
        """Create a new interview session"""
        try:
            session_id = str(uuid.uuid4())
            session_data.update({
                'session_id': session_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'status': 'pending'
            })
            
            session_ref = self.db.collection('interview_sessions').document(session_id)
            session_ref.set(session_data)
            logger.info(f"Interview session created: {session_id}")
            return session_id
        except Exception as e:
            logger.error(f"Error creating interview session: {e}")
            return None
    
    def get_interview_session(self, session_id):
        """Get interview session data"""
        try:
            session_ref = self.db.collection('interview_sessions').document(session_id)
            doc = session_ref.get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting interview session: {e}")
            return None
    
    def update_interview_session(self, session_id, update_data):
        """Update interview session"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            session_ref = self.db.collection('interview_sessions').document(session_id)
            session_ref.update(update_data)
            logger.info(f"Interview session updated: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating interview session: {e}")
            return False
    
    # ==================== INTERVIEW MANAGEMENT ====================
    
    def create_interview(self, interview_data):
        """Create a new interview record"""
        try:
            interview_id = str(uuid.uuid4())
            interview_data.update({
                'interview_id': interview_id,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            interview_ref = self.db.collection('interviews').document(interview_id)
            interview_ref.set(interview_data)
            logger.info(f"Interview created with ID: {interview_id}")
            return interview_id
        except Exception as e:
            logger.error(f"Error creating interview: {e}")
            return None
    
    def get_interview(self, interview_id):
        """Get interview details by ID"""
        try:
            interview_ref = self.db.collection('interviews').document(interview_id)
            doc = interview_ref.get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting interview: {e}")
            return None
    
    def get_user_interviews(self, user_id, limit=50):
        """Get all interviews for a specific user"""
        try:
            interviews_ref = self.db.collection('interviews')
            query = interviews_ref.where('user_id', '==', user_id).limit(limit)
            docs = query.stream()
            
            interviews = []
            for doc in docs:
                interview_data = {'id': doc.id, **doc.to_dict()}
                interviews.append(interview_data)
            
            # Sort by created_at in Python since Firestore composite index might not be set up
            interviews.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logger.info(f"Retrieved {len(interviews)} interviews for user: {user_id}")
            return interviews
        except Exception as e:
            logger.error(f"Error getting user interviews: {e}")
            return []
    
    def update_interview(self, interview_id, update_data):
        """Update interview record"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            interview_ref = self.db.collection('interviews').document(interview_id)
            interview_ref.update(update_data)
            logger.info(f"Interview updated: {interview_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating interview: {e}")
            return False
    
    def delete_interview(self, interview_id):
        """Delete an interview record"""
        try:
            interview_ref = self.db.collection('interviews').document(interview_id)
            interview_ref.delete()
            logger.info(f"Interview deleted: {interview_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting interview: {e}")
            return False
    
    def save_analysis_data(self, analysis_data):
        """Save analysis data for an interview"""
        try:
            analysis_id = str(uuid.uuid4())
            analysis_data.update({
                'analysis_id': analysis_id,
                'saved_at': datetime.now().isoformat()
            })
            
            analysis_ref = self.db.collection('interview_analysis').document(analysis_id)
            analysis_ref.set(analysis_data)
            
            # Also save to realtime database for live updates
            interview_id = analysis_data.get('interview_id')
            if interview_id:
                rtdb_ref = self.rtdb.reference(f'interviews/{interview_id}/analysis')
                rtdb_ref.push(analysis_data)
            
            logger.info(f"Analysis data saved with ID: {analysis_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis data: {e}")
            return False
    
    def get_interview_analysis(self, interview_id):
        """Get all analysis data for an interview"""
        try:
            analysis_ref = self.db.collection('interview_analysis')
            query = analysis_ref.where('interview_id', '==', interview_id).order_by('timestamp')
            docs = query.stream()
            
            analysis_data = []
            for doc in docs:
                data = {'id': doc.id, **doc.to_dict()}
                analysis_data.append(data)
            
            logger.info(f"Retrieved {len(analysis_data)} analysis records for interview: {interview_id}")
            return analysis_data
        except Exception as e:
            logger.error(f"Error getting interview analysis: {e}")
            return []

    # ==================== REAL-TIME ANALYSIS DATA ====================
    
    def save_realtime_analysis(self, session_id, analysis_data):
        """Save real-time analysis data to Firebase Realtime Database"""
        try:
            timestamp = datetime.now().isoformat()
            
            logger.info(f"🔥 Attempting to save to Realtime DB for session: {session_id}")
            
            # Use the helper method to get proper references
            ref = self._get_rtdb_reference(f'sessions/{session_id}/analysis')
            if not ref:
                logger.error(f"❌ Could not get rtdb reference for session: {session_id}")
                return None
            
            # Prepare data for Realtime DB
            rtdb_data = {
                'timestamp': timestamp,
                'session_id': session_id,
                **analysis_data
            }
            
            logger.info(f"📝 Pushing data to path: sessions/{session_id}/analysis")
            new_analysis_ref = ref.push(rtdb_data)
            
            logger.info(f"✅ Data pushed successfully, key: {new_analysis_ref.key}")
            
            # Also update latest analysis summary
            latest_ref = self._get_rtdb_reference(f'sessions/{session_id}/latest_analysis')
            if latest_ref:
                latest_data = {
                    'timestamp': timestamp,
                    'face_stress': analysis_data.get('face_stress', {}),
                    'hand_confidence': analysis_data.get('hand_confidence', {}),  # Fixed key name
                    'eye_confidence': analysis_data.get('eye_confidence', {}),    # Fixed key name
                    'voice_confidence': analysis_data.get('voice_confidence', {}), # Fixed key name
                    'overall': analysis_data.get('overall', {})
                }
                
                logger.info(f"📝 Setting latest analysis data...")
                latest_ref.set(latest_data)
                logger.info(f"✅ Latest analysis updated successfully")
            
            logger.info(f"✅ Real-time analysis saved for session: {session_id}, key: {new_analysis_ref.key}")
            return new_analysis_ref.key
            
        except Exception as e:
            logger.error(f"❌ Error saving real-time analysis: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            
            # Return None but don't fail the entire operation
            return None
    
    def get_realtime_analysis(self, session_id, limit=100):
        """Get real-time analysis data for a session"""
        try:
            ref = self.rtdb.reference(f'sessions/{session_id}/analysis')
            data = ref.order_by_key().limit_to_last(limit).get()
            
            if data:
                return [{'key': k, **v} for k, v in data.items()]
            return []
        except Exception as e:
            logger.error(f"Error getting real-time analysis: {e}")
            return []
    
    def get_latest_analysis(self, session_id):
        """Get the latest analysis summary for a session"""
        try:
            ref = self.rtdb.reference(f'sessions/{session_id}/latest_analysis')
            data = ref.get()
            return data
        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None
    
    # ==================== LEGACY METHODS ====================
    
    
    
    
    def save_analysis_result(self, session_id, analysis_data):
        """Save real-time analysis results"""
        try:
            logger.info(f"💾 Attempting to save to Firestore collection 'analysis_results'")
            logger.info(f"📝 Data being saved: session_id={session_id}, keys={list(analysis_data.keys())}")
            
            # Prepare document data - use the analysis_data as-is to preserve binary values
            doc_data = analysis_data.copy()
            doc_data['session_id'] = session_id
            # Don't override timestamp if it already exists in analysis_data
            
            # Add document to collection
            result_ref = self.db.collection('analysis_results').add(doc_data)
            doc_id = result_ref[1].id
            
            logger.info(f"✅ Successfully saved to Firestore with doc_id: {doc_id}")
            logger.info(f"📍 Document path: analysis_results/{doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis result to Firestore: {e}")
            logger.error(f"❌ Error type: {type(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
    
    # DISABLED: Removed realtime_analysis collection save - only save to analysis_results
    def DISABLED_save_realtime_analysis(self, session_id, analysis_data):
        """Save real-time analysis results every 10 seconds - DISABLED"""
        try:
            # Create real-time analysis document
            realtime_data = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'analysis_interval': '10_seconds',
                'confidence_scores': {
                    'eye': analysis_data.get('eye_confidence', {}).get('confidence_level') == 'confident',
                    'hand': analysis_data.get('hand_confidence', {}).get('confidence_level') == 'confident',
                    'voice': analysis_data.get('voice_confidence', {}).get('confidence_level') == 'confident',
                    'overall': analysis_data.get('overall', {}).get('confidence_score', 0)
                },
                'stress_level': analysis_data.get('face_stress', {}).get('stress_level') == 'stress',
                'emotion': analysis_data.get('face_stress', {}).get('emotion', 'neutral'),
                'created_at': datetime.now().isoformat()
            }
            
            # Save to realtime_analysis collection
            doc_ref = self.db.collection('realtime_analysis').document()
            doc_ref.set(realtime_data)
            
            logger.info(f"🔄 Real-time analysis saved (10s interval) - doc_id: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"❌ Error saving real-time analysis: {e}")
            return None
    
    def get_session_results(self, session_id):
        """Get all analysis results for a session"""
        try:
            results = self.db.collection('analysis_results').where('session_id', '==', session_id).stream()
            return [doc.to_dict() for doc in results]
        except Exception as e:
            logger.error(f"Error getting session results: {e}")
            return []
    
    def get_user_sessions(self, user_id):
        """Get all sessions for a user"""
        try:
            sessions = self.db.collection('interview_sessions').where('user_id', '==', user_id).stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in sessions]
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    # ==================== JOB ROLE MANAGEMENT ====================
    
    def create_job_role(self, job_role_data):
        """Create a new job role"""
        try:
            job_role_id = str(uuid.uuid4())
            
            # Extract confidence levels and convert to weights
            confidence_levels = job_role_data.get('confidence_levels', {})
            voice_weight = confidence_levels.get('voice_confidence', 33.33)
            hand_weight = confidence_levels.get('hand_confidence', 33.33)
            eye_weight = confidence_levels.get('eye_confidence', 33.33)
            
            # Ensure weights sum to 100
            total_weight = voice_weight + hand_weight + eye_weight
            if total_weight != 100:
                # Normalize weights
                voice_weight = (voice_weight / total_weight) * 100
                hand_weight = (hand_weight / total_weight) * 100
                eye_weight = (eye_weight / total_weight) * 100
            
            job_role_data.update({
                'job_role_id': job_role_id,
                'voice_confidence_weight': voice_weight,
                'hand_confidence_weight': hand_weight,
                'eye_confidence_weight': eye_weight,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            job_role_ref = self.db.collection('job_roles').document(job_role_id)
            job_role_ref.set(job_role_data)
            logger.info(f"Job role created with ID: {job_role_id}")
            return job_role_id
        except Exception as e:
            logger.error(f"Error creating job role: {e}")
            return None
    
    def get_job_role(self, job_role_id):
        """Get job role by ID"""
        try:
            job_role_ref = self.db.collection('job_roles').document(job_role_id)
            doc = job_role_ref.get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting job role: {e}")
            return None
    
    def get_user_job_roles(self, user_id, limit=50):
        """Get all job roles for a specific user"""
        try:
            job_roles_ref = self.db.collection('job_roles')
            query = job_roles_ref.where('user_id', '==', user_id).limit(limit)
            docs = query.stream()
            
            job_roles = []
            for doc in docs:
                job_role_data = {'id': doc.id, **doc.to_dict()}
                job_roles.append(job_role_data)
            
            # Sort by created_at in Python since Firestore composite index might not be set up
            job_roles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logger.info(f"Retrieved {len(job_roles)} job roles for user: {user_id}")
            return job_roles
        except Exception as e:
            logger.error(f"Error getting user job roles: {e}")
            return []
    
    def update_job_role(self, job_role_id, update_data):
        """Update job role"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            job_role_ref = self.db.collection('job_roles').document(job_role_id)
            job_role_ref.update(update_data)
            logger.info(f"Job role updated: {job_role_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating job role: {e}")
            return False
    
    def delete_job_role(self, job_role_id):
        """Delete job role"""
        try:
            job_role_ref = self.db.collection('job_roles').document(job_role_id)
            job_role_ref.delete()
            logger.info(f"Job role deleted: {job_role_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting job role: {e}")
            return False
    
    # ==================== CONFIDENCE & STRESS ANALYSIS ====================
    
    def save_confidence_analysis(self, analysis_data):
        """Save confidence analysis data"""
        try:
            analysis_id = str(uuid.uuid4())
            analysis_data['id'] = analysis_id
            
            # Save to Firestore
            analysis_ref = self.db.collection('confidence_analysis').document(analysis_id)
            analysis_ref.set(analysis_data)
            
            logger.info(f"Confidence analysis saved: {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving confidence analysis: {e}")
            return None
    
    def get_confidence_analysis(self, interview_id):
        """Get confidence analysis data for an interview"""
        try:
            analysis_ref = self.db.collection('confidence_analysis')
            query = analysis_ref.where('interview_id', '==', interview_id)
            docs = query.stream()
            
            analysis_data = []
            for doc in docs:
                data = doc.to_dict()
                analysis_data.append(data)
            
            return analysis_data
        except Exception as e:
            logger.error(f"Error getting confidence analysis: {e}")
            return []
    
    def save_stress_analysis(self, analysis_data):
        """Save stress analysis data"""
        try:
            analysis_id = str(uuid.uuid4())
            analysis_data['id'] = analysis_id
            
            # Save to Firestore
            analysis_ref = self.db.collection('stress_analysis').document(analysis_id)
            analysis_ref.set(analysis_data)
            
            logger.info(f"Stress analysis saved: {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving stress analysis: {e}")
            return None
    
    def get_stress_analysis(self, interview_id):
        """Get stress analysis data for an interview"""
        try:
            analysis_ref = self.db.collection('stress_analysis')
            query = analysis_ref.where('interview_id', '==', interview_id)
            docs = query.stream()
            
            analysis_data = []
            for doc in docs:
                data = doc.to_dict()
                analysis_data.append(data)
            
            return analysis_data
        except Exception as e:
            logger.error(f"Error getting stress analysis: {e}")
            return []
    
    def save_final_analysis(self, analysis_data):
        """Save final analysis results"""
        try:
            analysis_id = str(uuid.uuid4())
            analysis_data['id'] = analysis_id
            
            # Save to Firestore
            analysis_ref = self.db.collection('final_analysis').document(analysis_id)
            analysis_ref.set(analysis_data)
            
            # Also update the interview record with final scores
            interview_ref = self.db.collection('interviews').document(analysis_data['interview_id'])
            interview_ref.update({
                'final_confidence_score': analysis_data['final_confidence_score'],
                'final_stress_score': analysis_data['final_stress_score'],
                'analysis_completed': True,
                'analysis_completed_at': datetime.now().isoformat()
            })
            
            logger.info(f"Final analysis saved: {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving final analysis: {e}")
            return None
    
    def get_final_analysis(self, interview_id):
        """Get final analysis results for an interview"""
        try:
            analysis_ref = self.db.collection('final_analysis')
            query = analysis_ref.where('interview_id', '==', interview_id)
            docs = query.stream()
            
            analysis_data = []
            for doc in docs:
                data = doc.to_dict()
                analysis_data.append(data)
            
            return analysis_data[0] if analysis_data else None
        except Exception as e:
            logger.error(f"Error getting final analysis: {e}")
            return None
    
    def get_analysis_results(self, interview_id):
        """Get all analysis results for an interview from analysis_results collection"""
        try:
            analysis_ref = self.db.collection('analysis_results')
            query = analysis_ref.where('interview_id', '==', interview_id)
            docs = query.stream()
            
            analysis_data = []
            for doc in docs:
                data = doc.to_dict()
                analysis_data.append(data)
            
            return analysis_data
        except Exception as e:
            logger.error(f"Error getting analysis results: {e}")
            return []

    # ==================== FINAL SCORES MANAGEMENT ====================
    
    def save_final_scores(self, session_id, user_id, job_role_id, final_scores, timestamp=None):
        """Save final interview scores to database"""
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            final_scores_data = {
                'session_id': session_id,
                'user_id': user_id,
                'job_role_id': job_role_id,
                'final_scores': final_scores,
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat()
            }
            
            # Save to Firestore
            final_scores_ref = self.db.collection('final_scores').document(session_id)
            final_scores_ref.set(final_scores_data)
            
            logger.info(f"Final scores saved for session {session_id}")
            return final_scores_data
            
        except Exception as e:
            logger.error(f"Error saving final scores: {e}")
            return None
    
    def get_final_scores(self, session_id):
        """Get final scores for a specific session"""
        try:
            final_scores_ref = self.db.collection('final_scores').document(session_id)
            doc = final_scores_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting final scores: {e}")
            return None
    
    def get_user_final_scores(self, user_id):
        """Get all final scores for a user"""
        try:
            final_scores_ref = self.db.collection('final_scores')
            query = final_scores_ref.where('user_id', '==', user_id).order_by('created_at', direction='DESCENDING')
            docs = query.stream()
            
            scores = []
            for doc in docs:
                data = doc.to_dict()
                scores.append(data)
            
            return scores
            
        except Exception as e:
            logger.error(f"Error getting user final scores: {e}")
            return []
    
    def get_interview_records(self, session_id):
        """Get all interview records for scoring calculation"""
        try:
            # Get records from Firestore (where real-time analyzer saves data)
            analysis_ref = self.db.collection('analysis_results')
            query = analysis_ref.where('session_id', '==', session_id)
            docs = query.stream()
            
            records = []
            for doc in docs:
                data = doc.to_dict()
                # Only include records that have the required analysis components
                if all(key in data for key in ['overall', 'eye_confidence', 'face_stress', 'hand_confidence', 'voice_confidence']):
                    records.append(data)
            
            # Sort by timestamp
            records.sort(key=lambda x: x.get('timestamp', ''))
            logger.info(f"Retrieved {len(records)} interview records for session {session_id}")
            return records
            
        except Exception as e:
            logger.error(f"Error getting interview records: {e}")
            return []
