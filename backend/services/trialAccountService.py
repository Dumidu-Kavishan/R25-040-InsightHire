# Trial Account Service for InsightHire Backend
import uuid
import random
import string
from datetime import datetime, timedelta
from utils.database import DatabaseManager
import firebase_admin
from firebase_admin import auth
import logging

logger = logging.getLogger(__name__)

class TrialAccountService:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def generate_trial_id(self):
        """Generate a unique trial account ID like '01ab12'"""
        chars = '0123456789abcdef'
        result = ''
        for i in range(6):
            result += chars[random.randint(0, len(chars) - 1)]
        return result

    def generate_trial_password(self):
        """Generate a random password for trial account"""
        chars = string.ascii_letters + string.digits + '!@#$%'
        result = ''
        for i in range(12):
            result += chars[random.randint(0, len(chars) - 1)]
        return result

    def create_trial_account(self):
        """Create a trial account"""
        try:
            trial_id = self.generate_trial_id()
            username = f"trial_{trial_id}"
            email = f"{username}@trial.insighthire.com"
            password = self.generate_trial_password()

            # Create Firebase user
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=f"Trial User {trial_id.upper()}"
            )

            # Create user profile in database
            profile_data = {
                'user_id': user_record.uid,
                'email': email,
                'username': username,
                'display_name': f"Trial User {trial_id.upper()}",
                'account_type': 'trial',
                'trial_id': trial_id,
                'trial_created_at': datetime.now().isoformat(),
                'trial_expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
                'interview_limit': 2,
                'job_role_limit': 2,
                'interviews_used': 0,
                'job_roles_used': 0,
                'is_active': True
            }

            profile_id = self.db_manager.create_user_profile(profile_data)

            return {
                'success': True,
                'trial_account': {
                    'trial_id': trial_id,
                    'username': username,
                    'email': email,
                    'password': password,
                    'display_name': f"Trial User {trial_id.upper()}",
                    'interview_limit': 2,
                    'job_role_limit': 2,
                    'expires_at': profile_data['trial_expires_at']
                }
            }

        except Exception as e:
            logger.error(f"Error creating trial account: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def check_interview_limit(self, user_id):
        """Check if user can create more interviews"""
        try:
            profile = self.db_manager.get_user_profile(user_id)
            
            if not profile or profile.get('account_type') != 'trial':
                return {'can_create': True, 'reason': 'Not a trial account'}

            interviews_used = profile.get('interviews_used', 0)
            interview_limit = profile.get('interview_limit', 2)

            if interviews_used >= interview_limit:
                return { 
                    'can_create': False, 
                    'reason': 'Trial interview limit reached',
                    'limit': interview_limit,
                    'used': interviews_used
                }

            return { 
                'can_create': True, 
                'limit': interview_limit,
                'used': interviews_used,
                'remaining': interview_limit - interviews_used
            }

        except Exception as e:
            logger.error(f"Error checking interview limit: {e}")
            return {'can_create': False, 'error': str(e)}

    def check_job_role_limit(self, user_id):
        """Check if user can create more job roles"""
        try:
            profile = self.db_manager.get_user_profile(user_id)
            
            if not profile or profile.get('account_type') != 'trial':
                return {'can_create': True, 'reason': 'Not a trial account'}

            job_roles_used = profile.get('job_roles_used', 0)
            job_role_limit = profile.get('job_role_limit', 2)

            if job_roles_used >= job_role_limit:
                return { 
                    'can_create': False, 
                    'reason': 'Trial job role limit reached',
                    'limit': job_role_limit,
                    'used': job_roles_used
                }

            return { 
                'can_create': True, 
                'limit': job_role_limit,
                'used': job_roles_used,
                'remaining': job_role_limit - job_roles_used
            }

        except Exception as e:
            logger.error(f"Error checking job role limit: {e}")
            return {'can_create': False, 'error': str(e)}

    def increment_interview_usage(self, user_id):
        """Increment interview usage for trial account"""
        try:
            profile = self.db_manager.get_user_profile(user_id)
            
            if profile and profile.get('account_type') == 'trial':
                update_data = {
                    'interviews_used': (profile.get('interviews_used', 0)) + 1
                }
                return self.db_manager.update_user_profile(user_id, update_data)
            
            return True  # Not a trial account, no limit
        except Exception as e:
            logger.error(f"Error incrementing interview usage: {e}")
            return False

    def increment_job_role_usage(self, user_id):
        """Increment job role usage for trial account"""
        try:
            profile = self.db_manager.get_user_profile(user_id)
            
            if profile and profile.get('account_type') == 'trial':
                update_data = {
                    'job_roles_used': (profile.get('job_roles_used', 0)) + 1
                }
                return self.db_manager.update_user_profile(user_id, update_data)
            
            return True  # Not a trial account, no limit
        except Exception as e:
            logger.error(f"Error incrementing job role usage: {e}")
            return False

    def get_trial_status(self, user_id):
        """Get trial account status"""
        try:
            profile = self.db_manager.get_user_profile(user_id)
            
            if not profile or profile.get('account_type') != 'trial':
                return {'is_trial': False}

            now = datetime.now()
            expires_at = datetime.fromisoformat(profile.get('trial_expires_at', ''))
            is_expired = now > expires_at

            return {
                'is_trial': True,
                'trial_id': profile.get('trial_id'),
                'expires_at': profile.get('trial_expires_at'),
                'is_expired': is_expired,
                'interview_limit': profile.get('interview_limit', 2),
                'job_role_limit': profile.get('job_role_limit', 2),
                'interviews_used': profile.get('interviews_used', 0),
                'job_roles_used': profile.get('job_roles_used', 0),
                'interviews_remaining': profile.get('interview_limit', 2) - profile.get('interviews_used', 0),
                'job_roles_remaining': profile.get('job_role_limit', 2) - profile.get('job_roles_used', 0)
            }

        except Exception as e:
            logger.error(f"Error getting trial status: {e}")
            return {'is_trial': False, 'error': str(e)}
