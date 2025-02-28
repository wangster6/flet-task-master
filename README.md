# Flet Task Master
Hosted at: [https://flettaskmaster.publicvm.com/](https://flettaskmaster.publicvm.com/)
<br>

A cloud-powered, full-stack to-do list application built using Flet and Supabase, deployed on an AWS EC2 instance with robust security configurations and backend integrations.
<br><br>

## Features
- **Cloud-Based Storage:** All tasks are stored persistently with real-time updates and automatic synchronization.
- **Secure Deployment:** The application is hosted on a remote cloud instance with controlled access and strict security policies.
- **Credential Security:** No sensitive credentials are hardcoded—secrets are dynamically retrieved from a secure storage system.
- **Priority-Based Task Management:** Users can assign and view task priorities (High, Medium, Low) with color-coded labels.
- **Automatic Task Sorting:** Tasks are sorted dynamically so that high-priority tasks appear at the top of the list.
- **Fully Responsive UI:** Optimized for both desktop and mobile devices, ensuring seamless usability across different screen sizes.
- **Persistent Uptime:** The app remains running even after SSH sessions are closed, ensuring uninterrupted availability.
- **Scalable Web Access:** A reverse proxy efficiently routes user requests, improving performance and scalability.
- **End-to-End Encryption:** All web traffic is secured with HTTPS, ensuring safe and encrypted communication.
- **Mobile Optimizations:** Editing a task automatically triggers the on-screen keyboard for a smoother mobile experience.
- **Error Handling & Stability:** The system gracefully handles network failures and database errors to prevent crashes.
<br>

## Technologies & Tools Used

### **Frontend & UI Framework**
- **Flet** (`0.26.0`) – Python-based UI framework to create interactive web and desktop apps.
- **Flet Web/Desktop** – Supports both web-based and local desktop UI rendering.

### **Backend & API**
- **Supabase (`2.13.0`)** – PostgreSQL-based backend for storing tasks.
- **boto3 (`1.37.2`)** – AWS SDK for securely fetching secrets.

### **Deployment & Cloud Infrastructure**
- **AWS EC2 (Amazon Linux 2023)** – Hosting the application.
- **AWS Security Group** – Restricted inbound and outbound access.
- **AWS Systems Manager (SSM) Parameter Store** – Secure credential storage.
- **tmux** – Persistent process management for the running Flet app.
- **Nginx** – Reverse proxy setup for handling web requests.

### **Security & Credential Management**
- **IAM User & Access Keys** – Restricted API access for fetching secrets.
- **SSL with Let's Encrypt (Certbot)** – Encrypted HTTPS communication.
<br>

## **Future Enhancements**
✅ Priority-based auto-sorting <br>
🔲 Task editing with priority changes <br>
🔲 Advanced styling for a polished UI <br>
🔲 User authentication & multi-user support <br>
🔲 Task categories for organization <br>
<br>

## Contributing
Contributions to this project are welcome! Feel free to submit issues or pull requests.
<br><br>

## Contact
For questions or feedback, please contact me on [my profile](https://github.com/wangster6).
<br><br>

## Contributors
<a href="https://github.com/wangster6/flet-task-master/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=wangster6/flet-task-master" />
</a>
