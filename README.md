# GrocerEase

GrocerEase is a web application that helps users compare grocery item prices across multiple Kroger locations. It fetches real-time product data using the Kroger API and helps users build, manage, and compare shopping lists for cost-effective grocery shopping.

## Features

- User authentication (signup, login, logout)
- Search for grocery items using Kroger API
- Add and manage a personalized shopping list
- View item prices across multiple Kroger stores
- See which store offers the cheapest overall list total
- Identify missing prices per store
- Admin interface for store inventory management

## Technologies Used

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS
- **Database:** PostgreSQL (hosted on AWS RDS)
- **Deployment:** AWS EC2 (Ubuntu)
- **API Integration:** Kroger Product API
- **Hosting:** AWS (EC2 for app, RDS for database)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Devorah135/GrocerEase.git
   cd GrocerEase

2. **Create a virtual environment**
   ```bash
    python -m venv venv
    source venv/bin/activate  # or `venv\Scripts\activate` on Windows

3. **Install dependencies**
   ```bash
    pip install -r requirements.txt


4. **Set environment variables**
     Create a .env file or set environment variables in your OS:
   ```env
    KROGER_CLIENT_ID=your-client-id
    KROGER_CLIENT_SECRET=your-client-secret

5. **Configure PostgreSQL database**
      Configure database credentials in settings.py to match your AWS RDS setup.

6. **Apply migrations**
   ```bash
    python manage.py migrate
  
7. **Run the development server**
   ```bash
    python manage.py runserver

*Kroger API Integration*
The app uses the Kroger OAuth 2.0 client credentials flow to obtain access tokens. Product and location data are fetched using the /products and /locations endpoints, respectively.

*License*
This project is for academic purposes and not licensed for commercial use.
