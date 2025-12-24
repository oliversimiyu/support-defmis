# Automated Responses Feature - DEFMIS

## Overview
The DEFMIS chat platform includes intelligent automated responses specifically designed for the Defence Forces Insurance Scheme. These responses help members get instant answers about coverage, claims, accredited hospitals, Smart Access app, and other insurance-related queries.

## DEFMIS-Specific Features

### Automated Response Categories

1. **Coverage & Benefits**
   - Inpatient coverage (100% up to KES 2M)
   - Outpatient coverage (75% up to KES 400K)
   - Annual limits and co-payment information

2. **Smart Access App**
   - App download instructions
   - USSD code (*891#) information
   - Visit code generation
   - OTP and biometric verification

3. **Hospital & Treatment**
   - Accredited hospital information
   - Emergency procedures
   - Non-accredited facility guidelines

4. **Claims & Pre-authorization**
   - Pre-authorization requirements
   - 24-hour notification rules
   - Claim form procedures

5. **Membership & Cards**
   - Card usage requirements
   - Fingerprint biometric verification
   - Lost card procedures

6. **Dependents & Family**
   - Spouse lifetime coverage
   - Children coverage (up to 21 years)
   - Dependent card requirements

7. **Exclusions**
   - Cosmetic procedures
   - Overseas treatment
   - Dental cosmetics
   - Other exclusions per Trust Deed

8. **Overseas Treatment**
   - Board approval process
   - Required documentation (3 opinions)
   - Processing timelines

9. **Emergency Support**
   - Emergency care procedures
   - Ambulance coverage rules
   - Urgent case handling

10. **Contact Information**
    - Smart Access support numbers
    - ICT support contacts
    - DEFMIS website

## Default Responses

The system comes with 15 pre-configured DEFMIS-specific automated responses:

1. **First Message (Welcome)**
   - Automatically greets customers when they send their first message
   - Helps set expectations and show immediate responsiveness

2. **Greeting Messages**
   - Detects greeting keywords (hello, hi, hey, good morning, etc.)
   - Responds with a friendly acknowledgment

3. **Keyword Matching**
   - Matches specific keywords in customer messages
   - Can be customized for different topics (pricing, support, account issues, etc.)
   - Supports comma-separated keyword lists

4. **Business Hours**
   - Automatically triggers when customers message outside business hours
   - Business hours: Monday-Friday, 9 AM - 5 PM
   - Lets customers know when to expect a response

5. **Offline Agents**
   - Triggers when no admin users are available
   - Manages customer expectations during high-volume periods

## Configuration

### Managing Automated Responses

Access the Django admin panel at `/admin/chat/automatedresponse/` to:

- Create new automated responses
- Edit existing responses
- Enable/disable responses
- Set priority levels (higher priority = checked first)
- Configure delay times (0 for immediate, or seconds to wait)

### Response Fields

- **Name**: Internal identifier for the response
- **Trigger Type**: When the response should trigger
- **Keywords**: Comma-separated keywords (for keyword trigger type)
- **Response Message**: The message to send to customers
- **Is Active**: Enable/disable the response
- **Priority**: Higher numbers are checked first (0-100)
- **Delay Seconds**: Wait time before sending (creates more natural interaction)

## Default Responses

The system comes with 15 pre-configured DEFMIS-specific automated responses:

1. **Welcome Message** (first_message) - DEFMIS introduction
2. **Greeting Response** (greeting) - Friendly greeting
3. **Coverage Information** (keyword) - Inpatient/outpatient coverage details
4. **Smart Access App** (keyword) - App and USSD information
5. **Hospital Information** (keyword) - Accredited hospitals guidance
6. **Pre-authorization** (keyword) - Admission approval process
7. **Claims Process** (keyword) - Claim form and payment procedures
8. **Membership Card** (keyword) - Card usage and biometrics
9. **Dependent Coverage** (keyword) - Family member coverage
10. **Exclusions** (keyword) - What's not covered
11. **Overseas Treatment** (keyword) - International care approval
12. **Emergency Help** (keyword) - Emergency procedures
13. **Contact Information** (keyword) - DEFMIS contact numbers
14. **Outside Business Hours** (business_hours) - After-hours message
15. **All Agents Offline** (offline) - When agents are busy

## Trigger Types

### Creating Custom Responses

```python
from chat.models import AutomatedResponse

# Create a refund policy response
AutomatedResponse.objects.create(
    name='Refund Policy',
    trigger_type='keyword',
    keywords='refund, return, money back, cancel subscription',
    response_message='Our refund policy allows returns within 30 days. An agent will provide you with specific details for your situation.',
    is_active=True,
    priority=80,
    delay_seconds=1
)
```

### Via Django Admin

1. Navigate to `/admin/chat/automatedresponse/add/`
2. Fill in the form fields
3. Save the automated response
4. It will immediately be active if "Is Active" is checked

## Monitoring

### Response Logs

All triggered automated responses are logged in the `AutomatedResponseLog` model:

- View logs at `/admin/chat/automatedresponselog/`
- See which messages triggered which responses
- Track automated response effectiveness
- Logs include chat session, trigger message, and timestamp

### Analytics

Monitor automated response performance:
- Check how often each response triggers
- Identify common customer questions
- Optimize keyword lists based on actual usage

## Best Practices

1. **Keep responses concise** - Short, helpful messages work best
2. **Use appropriate delays** - 1-3 seconds feels more natural than instant
3. **Avoid over-automation** - Too many responses can feel impersonal
4. **Set clear priorities** - Ensure the most relevant response triggers first
5. **Update regularly** - Review logs and adjust keywords/messages based on usage
6. **Test thoroughly** - Try different customer messages to ensure responses trigger correctly

## Technical Details

### Integration Points

- **Consumer**: `chat/consumers.py` - ChatConsumer triggers automated responses
- **Service**: `chat/automated_responses.py` - AutomatedResponseService handles logic
- **Models**: `chat/models.py` - AutomatedResponse and AutomatedResponseLog
- **Admin**: `chat/admin.py` - Django admin configuration

### Response Processing Flow

1. Customer sends a message via WebSocket
2. Message is saved to database
3. `AutomatedResponseService.process_automated_responses()` is called
4. Service checks all active automated responses
5. Matching responses are sent with configured delays
6. Each sent response is logged in AutomatedResponseLog

### Async/Await

The automated response system uses Django Channels' async capabilities:
- All database queries use `@database_sync_to_async` decorator
- Delays use `await asyncio.sleep()` for non-blocking waits
- Messages sent via WebSocket groups

## API

No additional API endpoints are needed. Automated responses work transparently through the existing WebSocket connection.

## Future Enhancements

Potential improvements:
- Machine learning-based response suggestions
- A/B testing for different response variations
- Response templates with variable substitution
- Time-based scheduling (different responses for different times)
- Customer sentiment analysis for response selection
- Multi-language support
