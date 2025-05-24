# PricePulse Deployment Guide

This guide will walk you through deploying PricePulse to Vercel with Neon PostgreSQL integration.

## Prerequisites

- GitHub account
- Vercel account
- Neon account (for PostgreSQL database)
- Node.js 16+ installed locally
- Python 3.10+ installed locally

## Step 1: Database Setup (Neon PostgreSQL)

1. **Create a Neon Project**:
   - Go to [Neon Console](https://console.neon.tech/)
   - Create a new project
   - Note down your connection string

2. **Set up Database Schema**:
   - The database tables will be created automatically when you first run the application
   - Or you can run the SQL scripts provided in the project

## Step 2: Backend Deployment (Vercel)

1. **Prepare the Backend**:
   \`\`\`bash
   cd backend
   # Ensure all dependencies are in requirements.txt
   pip freeze > requirements.txt
   \`\`\`

2. **Create Vercel Project for Backend**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Set the root directory to `backend`
   - Configure the following settings:
     - Framework Preset: Other
     - Build Command: `pip install -r requirements.txt`
     - Output Directory: (leave empty)
     - Install Command: (leave empty)

3. **Configure Environment Variables**:
   In your Vercel project settings, add these environment variables:
   \`\`\`
   DATABASE_URL=your_neon_connection_string
   FLASK_ENV=production
   PRICE_CHECK_INTERVAL=30
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SENDER_EMAIL=pricepulse@yourdomain.com
   ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
   CRON_SECRET=your_secure_random_string
   API_URL=https://your-backend-domain.vercel.app
   \`\`\`

4. **Deploy the Backend**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Note down your backend URL (e.g., `https://pricepulse-backend.vercel.app`)

## Step 3: Frontend Deployment (Vercel)

1. **Prepare the Frontend**:
   \`\`\`bash
   cd frontend
   npm install
   npm run build  # Test the build locally
   \`\`\`

2. **Create Vercel Project for Frontend**:
   - Create another new project on Vercel
   - Import the same GitHub repository
   - Set the root directory to `frontend`
   - Configure the following settings:
     - Framework Preset: Vite
     - Build Command: `npm run build`
     - Output Directory: `dist`
     - Install Command: `npm install`

3. **Configure Environment Variables**:
   \`\`\`
   VITE_API_URL=https://your-backend-domain.vercel.app/api
   \`\`\`

4. **Deploy the Frontend**:
   - Click "Deploy"
   - Wait for deployment to complete
   - Note down your frontend URL

## Step 4: Set Up Scheduled Price Updates

Since Vercel doesn't support background jobs, we'll use external cron services:

### Option 1: Vercel Cron Jobs (Recommended)

1. **Install Vercel CLI**:
   \`\`\`bash
   npm i -g vercel
   \`\`\`

2. **Create vercel.json in backend**:
   \`\`\`json
   {
     "crons": [
       {
         "path": "/api/cron",
         "schedule": "*/30 * * * *"
       }
     ]
   }
   \`\`\`

3. **Redeploy the backend** to activate cron jobs

### Option 2: External Cron Service

Use services like:
- [cron-job.org](https://cron-job.org)
- [EasyCron](https://www.easycron.com)
- [Cronhooks](https://cronhooks.io)

Set up a cron job to call:
\`\`\`
POST https://your-backend-domain.vercel.app/api/cron
Headers: Authorization: Bearer YOUR_CRON_SECRET
Schedule: Every 30 minutes
\`\`\`

## Step 5: Configure Email Alerts

1. **Gmail Setup** (Recommended for testing):
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password:
     - Go to Google Account settings
     - Security → 2-Step Verification → App passwords
     - Generate a password for "Mail"
   - Use this app password as `SMTP_PASSWORD`

2. **Production Email Setup**:
   For production, consider using:
   - [SendGrid](https://sendgrid.com)
   - [Mailgun](https://www.mailgun.com)
   - [Amazon SES](https://aws.amazon.com/ses/)

## Step 6: Domain Configuration (Optional)

1. **Custom Domain for Frontend**:
   - In Vercel dashboard, go to your frontend project
   - Settings → Domains
   - Add your custom domain

2. **Custom Domain for Backend**:
   - In Vercel dashboard, go to your backend project
   - Settings → Domains
   - Add your API subdomain (e.g., `api.yourdomain.com`)

3. **Update Environment Variables**:
   - Update `VITE_API_URL` in frontend
   - Update `ALLOWED_ORIGINS` in backend

## Step 7: Testing the Deployment

1. **Test the Frontend**:
   - Visit your frontend URL
   - Try adding a product
   - Check if the dashboard loads

2. **Test the Backend**:
   - Visit `https://your-backend-domain.vercel.app/api/health`
   - Should return `{"status": "OK"}`

3. **Test the Cron Job**:
   - Manually trigger: `POST https://your-backend-domain.vercel.app/api/cron`
   - Include the Authorization header with your CRON_SECRET

4. **Test Email Alerts**:
   - Add a product
   - Set a price alert above the current price
   - Manually trigger the cron job
   - Check if email is received

## Step 8: Monitoring and Maintenance

1. **Vercel Analytics**:
   - Enable Vercel Analytics for both projects
   - Monitor performance and usage

2. **Error Tracking**:
   - Consider integrating Sentry for error tracking
   - Add Sentry DSN to environment variables

3. **Database Monitoring**:
   - Monitor your Neon database usage
   - Set up alerts for connection limits

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**:
   - Verify DATABASE_URL is correct
   - Check Neon database is active
   - Ensure SSL is enabled

2. **CORS Errors**:
   - Verify ALLOWED_ORIGINS includes your frontend domain
   - Check if both HTTP and HTTPS are needed

3. **Email Not Sending**:
   - Verify SMTP credentials
   - Check if Gmail app password is correct
   - Test with a simple email service first

4. **Cron Job Not Working**:
   - Verify CRON_SECRET is set correctly
   - Check Vercel function logs
   - Test manual cron endpoint call

### Useful Commands:

\`\`\`bash
# Check Vercel deployment logs
vercel logs

# Test backend locally
cd backend && python app.py

# Test frontend locally
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build
\`\`\`

## Security Checklist

- [ ] All environment variables are set
- [ ] CRON_SECRET is a strong random string
- [ ] SMTP credentials are secure (use app passwords)
- [ ] CORS is configured for specific origins only
- [ ] Database connection uses SSL
- [ ] No sensitive data in client-side code

## Performance Optimization

- [ ] Enable Vercel Analytics
- [ ] Configure proper caching headers
- [ ] Optimize images and assets
- [ ] Monitor database query performance
- [ ] Set up CDN for static assets

Your PricePulse application should now be fully deployed and operational!
\`\`\`

Finally, let's create a comprehensive project completion checklist:
