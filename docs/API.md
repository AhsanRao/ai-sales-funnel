# API Documentation

## Endpoints

### Facebook Lead Webhook
- **URL**: `/webhook/facebook`
- **Method**: POST
- **Description**: Receives and processes new leads from Facebook

### Messenger Webhook
- **URL**: `/webhook/messenger`
- **Method**: POST
- **Description**: Handles incoming messages from Facebook Messenger

### Stripe Webhook
- **URL**: `/webhook/stripe`
- **Method**: POST
- **Description**: Processes Stripe payment events

## Request/Response Formats

### Facebook Lead Webhook
**Request**:
```json
{
  "id": "string",
  "campaign_id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "messenger_id": "string"
}
```

**Response**:
```json
{
  "status": "success",
  "lead_id": "integer"
}
```

### Messenger Webhook
**Request**:
```json
{
  "entry": [{
    "messaging": [{
      "sender": {
        "id": "string"
      },
      "message": {
        "text": "string"
      }
    }]
  }]
}
```

**Response**:
```json
{
  "status": "success"
}
```