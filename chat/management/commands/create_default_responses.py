"""
Management command to create default automated responses
"""
from django.core.management.base import BaseCommand
from chat.models import AutomatedResponse


class Command(BaseCommand):
    help = 'Creates default automated responses for the chat system'

    def handle(self, *args, **options):
        # First message welcome response
        AutomatedResponse.objects.get_or_create(
            name='Welcome Message',
            trigger_type='first_message',
            defaults={
                'response_message': 'Welcome! Thanks for reaching out. How can we assist you today?',
                'is_active': True,
                'priority': 100,
                'delay_seconds': 1,
            }
        )
        
        # Greeting response
        AutomatedResponse.objects.get_or_create(
            name='Greeting Response',
            trigger_type='greeting',
            defaults={
                'response_message': 'Hello! We\'re here to help. What can we do for you?',
                'is_active': True,
                'priority': 90,
                'delay_seconds': 0,
            }
        )
        
        # Pricing/Cost keywords
        AutomatedResponse.objects.get_or_create(
            name='Pricing Information',
            trigger_type='keyword',
            defaults={
                'keywords': 'pricing, price, cost, payment, pay, how much, billing, fee',
                'response_message': 'I see you\'re asking about pricing. Our team will provide you with detailed pricing information shortly. In the meantime, you can visit our pricing page or wait for an agent to assist you.',
                'is_active': True,
                'priority': 80,
                'delay_seconds': 2,
            }
        )
        
        # Support/Help keywords
        AutomatedResponse.objects.get_or_create(
            name='Support Help',
            trigger_type='keyword',
            defaults={
                'keywords': 'help, support, assistance, assist, problem, issue, error, bug',
                'response_message': 'I understand you need assistance. A support agent will be with you shortly to help resolve your issue. Please describe your problem in detail.',
                'is_active': True,
                'priority': 70,
                'delay_seconds': 1,
            }
        )
        
        # Account/Login keywords
        AutomatedResponse.objects.get_or_create(
            name='Account Issues',
            trigger_type='keyword',
            defaults={
                'keywords': 'account, login, password, username, sign in, access, forgot password',
                'response_message': 'For account-related issues, our support team will assist you. Please provide your email address and describe the issue you\'re experiencing.',
                'is_active': True,
                'priority': 75,
                'delay_seconds': 1,
            }
        )
        
        # Business hours response
        AutomatedResponse.objects.get_or_create(
            name='Outside Business Hours',
            trigger_type='business_hours',
            defaults={
                'response_message': 'Thank you for contacting us! Our business hours are Monday-Friday, 9 AM - 5 PM. Your message has been received and we\'ll respond as soon as we\'re back online.',
                'is_active': True,
                'priority': 95,
                'delay_seconds': 2,
            }
        )
        
        # Offline agents response
        AutomatedResponse.objects.get_or_create(
            name='All Agents Offline',
            trigger_type='offline',
            defaults={
                'response_message': 'All our agents are currently assisting other customers. Your message is important to us, and someone will respond to you as soon as possible.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 3,
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default automated responses')
        )
