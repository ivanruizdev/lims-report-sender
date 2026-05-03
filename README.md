# LIMS Report Sender 🧪📲

LIMS Report Sender is an open-source middleware designed to bridge the gap between legacy Laboratory Information Management Systems (LIMS) and modern communication platforms like WhatsApp (Official Cloud API) and Telegram.

It automates the delivery of clinical reports to patients, featuring a real-time monitoring dashboard and a robust Docker-based architecture.

## 🚀 Key Features

- Automated PDF Dispatch: Monitors local directories for new clinical reports and sends them instantly.
- Multi-Channel Support: Seamless integration with Telegram Bots and the Official WhatsApp Business API.
- Real-time Dashboard: Built with React and Tailwind CSS to monitor the delivery queue, active status, and historical logs.
- Legacy Compatibility: Designed to work with older LIMS (Java/PHP based) by connecting directly to the database or watching output folders.
- Secure & Private: Does not store patient data in the cloud. It queries your local Postgres database to match reports with patient contact info.
- Dockerized: Easy to deploy on any server (Windows, Linux, or Mac) using Docker Compose.

## 🏗️ Architecture

The system operates as a "Sidecar" application:

- LIMS generates a PDF report in a shared folder.
- LIMS-Bridge (Python) detects the new file.
- Database Query: The bot queries the local LIMS Postgres database to find the patient's phone number and preferred channel.
- Delivery: The report is sent via WhatsApp or Telegram.
- Monitoring: All activity is reflected in the React Dashboard.

## 🛠️ Tech Stack

- Backend: Python 3.10 (Watchdog, Psycopg2, Requests)
- Frontend: React.js + Tailwind CSS + Lucide Icons
- Database: PostgreSQL (Direct connection to LIMS)
- Containerization: Docker & Docker Compose
- Messaging APIs: WhatsApp Cloud API & Telegram Bot API

## 🚦 Getting Started

Prerequisites

- Docker and Docker Compose installed.
- Access to your LIMS PostgreSQL database.
- A WhatsApp Business Cloud API Token or a Telegram Bot Token.

### Installation

Clone the repository:

``` bash
git clone [https://github.com/ivanruizdev/LIMS-Bridge.git](https://github.com/ivanruizdev/LIMS-Bridge.git)
cd LIMS-Bridge
```

Configure Environment Variables:
Create a .env file based on the template:

``` bash
cp .env.example .env
```

Edit .env with your database credentials and API tokens.

Launch the system:

``` bash
docker-compose up -d --build
```

Access the Dashboard:
Open your browser at http://localhost:8080.

## ⚙️ Configuration (.env)

``` bash
# Database Configuration
DB_HOST=192.168.1.XX
DB_PORT=5432
DB_NAME=lims_db
DB_USER=postgres
DB_PASSWORD=your_password

# API Tokens
TELEGRAM_TOKEN=your_bot_token
WHATSAPP_TOKEN=your_meta_token
WHATSAPP_PHONE_ID=your_phone_id

# System Paths
WATCH_PATH=/app/reports/pdf_output
```

## 🗺️ Roadmap

- Direct PDF text scraping (for systems without DB access).
- Multi-tenant laboratory support.
- Advanced analytics dashboard (Success rates/Delivery times).
- Automatic retry logic for failed messages.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for suggestions and bug reports.

Developed with ❤️ for the clinical laboratory community.
