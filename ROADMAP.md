# Flet Task Master Roadmap

### 1️⃣ Initial Setup

✅ Installed and set up Flet.

✅ Created a basic UI for the to-do list app.

✅ Implemented an input field and an "Add Task" button.

✅ Displayed tasks dynamically when added.

### 2️⃣ UI Enhancements

✅ Styled and structured the UI for better usability.

✅ Made the task list scrollable when tasks exceed the screen height.

✅ Ensured long task names wrap properly instead of overflowing.

✅ Aligned input field & button to the bottom of the screen.

✅ Created a header for branding the app.

### 3️⃣ Task Functionality

✅ Implemented checkboxes for marking tasks as complete.

✅ Applied strikethrough styling when a task is completed.

✅ Implemented a delete button to remove tasks.

### 4️⃣ Database Integration (Supabase)

✅ Integrated Supabase for cloud-based persistent storage.

✅ Implemented loading tasks from Supabase when the app starts.

✅ Implemented database updates when tasks are marked as completed.

✅ Implemented database updates when tasks are deleted.

### 5️⃣ Database Optimization

✅ Prevented duplicate task entries (if user adds the same task multiple times) by enforcing case-insensitive uniqueness.

✅ Implemented error handling to handle network issues or API failures.

✅ Optimized Database Queries for Performance (Indexing)

### 6️⃣ Deployment

✅ Deployed the Flet app on an AWS EC2 instance.

✅ Configured tmux to keep the app running persistently, even after SSH disconnects.

✅ Installed and configured Nginx as a reverse proxy for the Flet web app.

✅ Set up a custom domain name (flettaskmaster.publicvm.com) for the web app.

✅ Configured DNS records to point the domain to the EC2 instance.

✅ Obtained and installed an SSL certificate using Let's Encrypt (certbot).

✅ Enabled HTTPS and forced HTTPS redirection for the domain in Nginx.

✅ Ensure Supabase credentials are securely stored in production (e.g., move .env file outside the repo, use AWS SSM Parameter Store/IAM roles).

### 7️⃣ UI Improvements & Features

✅ Add an "Edit Task" feature (allow users to modify existing tasks).

🔲 Add categories or priorities (e.g., high/medium/low priority).

🔲 Improve visual styling to make the app more appealing.

### 8️⃣ Final Testing & Documentation

🔲 Thoroughly test all features before deployment.

🔲 Write clear documentation for setting up the project.

🔲 Record a demo video for portfolio.

---

