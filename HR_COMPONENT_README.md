# HR Component - Job Role Management System

## Overview

The HR Component provides a comprehensive job role management system that allows HR professionals to define confidence level requirements for different job positions. This system integrates with the existing InsightHire interview monitoring platform to provide structured evaluation criteria based on voice, hand, and eye confidence levels.

## Features

### 🎯 Core Functionality

1. **Job Role Creation & Management**
   - Create custom job roles with specific confidence level requirements
   - Predefined job types (Software Engineer, Data Scientist, Product Manager, etc.)
   - Drag-and-drop sliders for confidence level configuration
   - Auto-calculation of eye confidence to ensure 100% total coverage

2. **Confidence Level Configuration**
   - **Voice Confidence**: Communication and speaking confidence (0-100%)
   - **Hand Confidence**: Gesture and body language confidence (0-100%)
   - **Eye Confidence**: Eye contact and visual engagement (0-100%)
   - **Total Validation**: Ensures all confidence levels sum to exactly 100%

3. **Interview Integration**
   - Assign job roles to specific interviews
   - Automatic confidence requirement application
   - Real-time evaluation against defined criteria

### 🎨 User Interface

1. **HR Dashboard** (`/hr-dashboard`)
   - Overview of all job roles
   - Quick statistics and metrics
   - Job role cards with confidence level display
   - Create, edit, and delete functionality

2. **HR Analytics** (`/hr-analytics`)
   - Tabbed interface with three sections:
     - **Job Role Management**: Full CRUD operations
     - **Interview Analytics**: Performance insights (coming soon)
     - **Confidence Analysis**: Advanced evaluation metrics (coming soon)

3. **Job Role Management Dialog**
   - Intuitive form with job type selection
   - Interactive sliders for confidence level configuration
   - Real-time validation and feedback
   - Visual indicators for confidence level distribution

## Technical Implementation

### Backend API Endpoints

```
POST   /api/job-roles              # Create new job role
GET    /api/job-roles              # Get all job roles for user
GET    /api/job-roles/{id}         # Get specific job role
PUT    /api/job-roles/{id}         # Update job role
DELETE /api/job-roles/{id}         # Delete job role
POST   /api/job-roles/{id}/assign  # Assign job role to interview
```

### Database Schema

**Job Roles Collection** (`job_roles`)
```json
{
  "id": "uuid",
  "user_id": "string",
  "name": "string",
  "description": "string",
  "confidence_levels": {
    "voice_confidence": 20,
    "hand_confidence": 30,
    "eye_confidence": 50
  },
  "is_active": true,
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

### Frontend Components

1. **HRDashboard.js** - Main dashboard for job role overview
2. **HRAnalytics.js** - Comprehensive analytics and management interface
3. **JobRoleManagement.js** - Modal dialog for creating/editing job roles
4. **jobRoleService.js** - API service for job role operations

## Usage Guide

### Creating a Job Role

1. Navigate to **HR Management** in the main navigation
2. Click **"Create Job Role"** button
3. Select a job type from the dropdown (or choose "Custom Role")
4. Fill in the job role name and description
5. Configure confidence levels using the interactive sliders:
   - Adjust voice and hand confidence as needed
   - Eye confidence is automatically calculated to ensure 100% total
6. Click **"Create Job Role"** to save

### Predefined Job Types

| Job Type | Voice | Hand | Eye | Use Case |
|----------|-------|------|-----|----------|
| Software Engineer | 20% | 30% | 50% | Technical roles requiring strong visual focus |
| Data Scientist | 25% | 25% | 50% | Analytical roles with balanced communication |
| Product Manager | 40% | 20% | 40% | Leadership roles requiring strong communication |
| UI/UX Designer | 15% | 45% | 40% | Creative roles emphasizing gesture and visual skills |
| Sales Representative | 50% | 20% | 30% | Communication-focused roles |
| Marketing Specialist | 35% | 25% | 40% | Balanced communication and creativity |

### Assigning Job Roles to Interviews

1. When creating a new interview, select a job role from the dropdown
2. The interview will automatically inherit the confidence level requirements
3. During the interview, candidate performance will be evaluated against these criteria
4. Post-interview analytics will show how well the candidate met the requirements

## Configuration

### Default Confidence Levels

The system provides sensible defaults for common job types, but HR professionals can customize these based on their specific requirements:

```javascript
const defaults = {
  'software_engineer': { voice: 20, hand: 30, eye: 50 },
  'data_scientist': { voice: 25, hand: 25, eye: 50 },
  'product_manager': { voice: 40, hand: 20, eye: 40 },
  'designer': { voice: 15, hand: 45, eye: 40 },
  'sales': { voice: 50, hand: 20, eye: 30 },
  'marketing': { voice: 35, hand: 25, eye: 40 }
};
```

### Validation Rules

- Total confidence levels must equal exactly 100%
- Individual confidence levels must be between 0-100%
- Job role names and descriptions are required
- Eye confidence is auto-calculated if not explicitly set

## Integration with Existing System

### Interview Creation
- Job role selection is now available in the interview creation dialog
- Selected job roles are stored with the interview record
- Confidence requirements are applied during real-time analysis

### Real-time Analysis
- The existing confidence detection system (voice, hand, eye) works seamlessly
- Results are compared against job role requirements
- Performance metrics are calculated based on defined criteria

### Analytics Integration
- Job role performance data is included in interview analytics
- HR can track how well candidates meet role-specific requirements
- Historical data helps refine confidence level requirements

## Testing

Run the test script to verify API functionality:

```bash
cd backend
python test_job_roles.py
```

The test script covers:
- Job role CRUD operations
- Confidence level validation
- Auto-calculation of eye confidence
- Error handling and edge cases

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Confidence level trend analysis
   - Role-specific performance benchmarks
   - Candidate comparison tools

2. **Smart Recommendations**
   - AI-powered confidence level suggestions
   - Industry benchmark integration
   - Performance-based role optimization

3. **Team Management**
   - Multi-user HR team support
   - Role-based permissions
   - Approval workflows

4. **Integration Features**
   - ATS (Applicant Tracking System) integration
   - Calendar scheduling with role requirements
   - Automated interview scoring

## Troubleshooting

### Common Issues

1. **Confidence levels don't sum to 100%**
   - Check that all three sliders are properly configured
   - Ensure eye confidence is not manually set when voice/hand are configured

2. **Job roles not appearing in interview creation**
   - Verify job roles are marked as active
   - Check user permissions and data loading

3. **API errors during job role creation**
   - Ensure backend server is running
   - Check Firebase configuration and permissions
   - Verify user authentication

### Support

For technical support or feature requests, please refer to the main InsightHire documentation or contact the development team.

## Conclusion

The HR Component provides a powerful and intuitive system for managing job role requirements and integrating them with the interview evaluation process. By defining specific confidence level requirements for different positions, HR professionals can ensure consistent and objective candidate evaluation while maintaining flexibility for role-specific needs.
