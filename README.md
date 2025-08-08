# Flask Birthday API - AWS ECS Deployment

A Python Flask application that manages user birthdays and provides birthday messages. The application offers both local development with SQLite and cloud deployment on AWS using ECS Fargate with DynamoDB.

## API Endpoints

The application exposes two main HTTP endpoints:

- **`PUT /hello/<username>`**: Saves or updates a user's date of birth
  - Request body: `{"dateOfBirth": "YYYY-MM-DD"}`
  - Response: `204 No Content` on success
  - Validates that username contains only letters and date is in the past

- **`GET /hello/<username>`**: Returns a personalized birthday message
  - Response: `200 OK` with JSON message
  - Returns birthday countdown or "Happy birthday!" if today is their birthday

- **`GET /health`**: Health check endpoint for load balancer monitoring
  - Response: `200 OK` with status message

## Project Structure

```
├── app.py              # Main Flask app for AWS deployment (uses DynamoDB)
├── applocal.py         # Local Flask app for development (uses SQLite)
├── requirements.txt    # Python dependencies (flask, boto3)
├── Dockerfile          # Container configuration for AWS deployment
├── setup.sh           # Script to create ECR repository and push Docker image
├── tests/
│   └── test_app.py    # Unit tests for the application
└── terraform/         # Infrastructure as Code for AWS deployment
    ├── main.tf        # Main Terraform configuration
    ├── variables.tf   # Variable definitions
    ├── outputs.tf     # Output definitions
    ├── provider.tf    # AWS provider configuration
    └── data.tf        # Data source definitions
```

## Architecture

### Local Development
- **Runtime**: Python 3.8+
- **Web Framework**: Flask 2.0+
- **Database**: SQLite3 (file-based)
- **Port**: 8000

### AWS Cloud Deployment
- **Container Platform**: AWS ECS Fargate
- **Database**: AWS DynamoDB
- **Load Balancer**: Application Load Balancer (ALB)
- **Networking**: VPC with public/private subnets across 2 AZs
- **Logging**: CloudWatch Logs
- **Auto Scaling**: CPU and Memory-based scaling (2-5 instances)
- **Container Registry**: Amazon ECR

## Requirements

### Local Development
- Python 3.8+
- Flask 2.0+
- SQLite3

### AWS Deployment
- AWS CLI configured
- Docker
- Terraform
- AWS Account with appropriate permissions

## Local Development

### Setup and Run
1. Install dependencies:
   ```bash
   pip install flask boto3
   ```

2. Run the local application:
   ```bash
   python applocal.py
   ```
   The application will start on `http://localhost:8000`

3. Run tests:
   ```bash
   python3 -m unittest tests/test_app.py
   ```

### Test the API
```bash
# Save a user's birthday
curl -X PUT http://localhost:8000/hello/john \
  -H "Content-Type: application/json" \
  -d '{"dateOfBirth": "1990-05-15"}'

# Get birthday message
curl http://localhost:8000/hello/john

# Health check
curl http://localhost:8000/health
```

## AWS Deployment

### Initial Setup
1. **Create ECR Repository and Push Image**:
   ```bash
   sh setup.sh
   ```
   This script will:
   - Create an ECR repository named `flask-docker-app-ayan`
   - Build and tag the Docker image
   - Push the image to ECR

2. **Deploy Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

### What Gets Deployed
- **VPC**: Custom VPC with public and private subnets across 2 availability zones
- **ECS Cluster**: Fargate cluster running the containerized application
- **Application Load Balancer**: Routes traffic to ECS tasks
- **DynamoDB Table**: `users` table with username as primary key
- **Security Groups**: Configured for ALB (port 80) and ECS (port 5000)
- **IAM Roles**: ECS task execution and service roles with DynamoDB permissions
- **CloudWatch**: Log group for application logs
- **Auto Scaling**: Automatic scaling based on CPU/memory utilization

### Accessing the Deployed Application
After deployment, Terraform outputs the ALB DNS name. Use this to access your application:
```bash
# Save a user's birthday
curl -X PUT http://your-alb-dns-name/hello/john \
  -H "Content-Type: application/json" \
  -d '{"dateOfBirth": "1990-05-15"}'

# Get birthday message
curl http://your-alb-dns-name/hello/john
```

## API Response Examples

### Successful Birthday Save
```bash
PUT /hello/alice
{"dateOfBirth": "1992-12-25"}
# Response: 204 No Content
```

### Birthday Messages
```json
// If birthday is today
{
  "message": "Hello, alice! Happy birthday!"
}

// If birthday is in 5 days
{
  "message": "Hello, alice! Your birthday is in 5 day(s)."
}

// If user not found
{
  "message": "User alice not found"
}
```

### Validation Errors
```json
// Invalid username (contains numbers/symbols)
{
  "error": "Username must contain only letters"
}

// Invalid date format
{
  "error": "Invalid date format. Use YYYY-MM-DD."
}

// Future date
{
  "error": "Date of birth must be in the past."
}
```

## Monitoring and Scaling

- **CloudWatch Logs**: Application logs are sent to CloudWatch log group `ecs-logs`
- **Health Checks**: ALB performs health checks on `/health` endpoint
- **Auto Scaling**: Automatically scales between 2-5 tasks based on:
  - CPU utilization > 50%
  - Memory utilization > 50%

## Cleanup

To destroy the AWS infrastructure:
```bash
cd terraform
terraform destroy --auto-approve

# Manually delete:
# - ECR repository: flask-docker-app-ayan
# - S3 bucket (if using remote state)
```

## Development Notes

- **app.py**: Production version that connects to DynamoDB
- **applocal.py**: Development version that uses local SQLite database
- The application includes comprehensive error handling and input validation
- Docker image uses Python 3.12 Alpine for minimal size
- Terraform creates a complete, production-ready AWS infrastructure