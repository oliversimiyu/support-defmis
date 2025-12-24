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
                'response_message': 'Welcome to DEFMIS (Defence Forces Insurance Scheme)! How may we assist you today? You can ask about coverage, claims, accredited hospitals, or the Smart Access app.',
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
                'response_message': 'Hello! Welcome to DEFMIS support. How can we help you with your medical insurance needs?',
                'is_active': True,
                'priority': 90,
                'delay_seconds': 0,
            }
        )
        
        # Coverage/Benefits information
        AutomatedResponse.objects.get_or_create(
            name='Coverage Information',
            trigger_type='keyword',
            defaults={
                'keywords': 'coverage, cover, benefit, benefits, limit, limits, how much, inpatient, outpatient, percentage',
                'response_message': 'DEFMIS Coverage: Inpatient - 100% up to KES 2,000,000 per year. Outpatient - 75% (you pay 25%) up to KES 400,000 per year. An agent will provide more details shortly.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 1,
            }
        )
        
        # Smart Access App
        AutomatedResponse.objects.get_or_create(
            name='Smart Access App',
            trigger_type='keyword',
            defaults={
                'keywords': 'app, smart access, download, *891#, ussd, registration, register, otp, visit code',
                'response_message': 'Smart Access App: Download from Google Play or Apple App Store, or dial *891#. Use it to monitor coverage, initiate hospital visits, and get visit codes. Need help? Call 0203206000 or 0709326000.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 1,
            }
        )
        
        # Hospital/Treatment queries
        AutomatedResponse.objects.get_or_create(
            name='Hospital Information',
            trigger_type='keyword',
            defaults={
                'keywords': 'hospital, hospitals, accredited, facility, facilities, treatment, where can i, which hospital',
                'response_message': 'Visit www.defmis.org for our list of accredited hospitals. Always carry your membership card and ID. For emergencies at non-accredited facilities, contact the MD or Management Team first.',
                'is_active': True,
                'priority': 80,
                'delay_seconds': 1,
            }
        )
        
        # Pre-authorization
        AutomatedResponse.objects.get_or_create(
            name='Pre-authorization',
            trigger_type='keyword',
            defaults={
                'keywords': 'pre-authorization, preauthorization, pre authorization, admission, admitted, admit, approval, approve, letter',
                'response_message': 'All admissions require pre-authorization from DEFMIS within 24 hours (except emergencies). The hospital will request this. Emergency cases must be reported within 24 hours.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 1,
            }
        )
        
        # Claims process
        AutomatedResponse.objects.get_or_create(
            name='Claims Process',
            trigger_type='keyword',
            defaults={
                'keywords': 'claim, claims, form, invoice, receipt, payment, pay, bill, billing',
                'response_message': 'Fill Part I of the DEFMIS claim form at hospital reception and sign it. Outpatient: You pay 25% at the facility. Inpatient: DEFMIS pays 100% directly to the hospital (within annual limits).',
                'is_active': True,
                'priority': 80,
                'delay_seconds': 1,
            }
        )
        
        # Card/Membership issues
        AutomatedResponse.objects.get_or_create(
            name='Membership Card',
            trigger_type='keyword',
            defaults={
                'keywords': 'card, membership card, lost card, forgot card, member card, id, identification, fingerprint, biometric',
                'response_message': 'Always carry your membership card and National ID. Verification uses fingerprint biometrics or OTP via Smart Access. Each dependent has their own card. For lost cards, contact our office.',
                'is_active': True,
                'priority': 80,
                'delay_seconds': 1,
            }
        )
        
        # Dependents/Family coverage
        AutomatedResponse.objects.get_or_create(
            name='Dependent Coverage',
            trigger_type='keyword',
            defaults={
                'keywords': 'dependent, dependants, children, child, spouse, wife, husband, family, kids, son, daughter, age limit',
                'response_message': 'Coverage: You & spouse for life. Children (must be single) covered until 21st birthday. Each dependent needs their own card. Children under 6 are linked to parent/guardian in Smart Access.',
                'is_active': True,
                'priority': 80,
                'delay_seconds': 1,
            }
        )
        
        # Exclusions
        AutomatedResponse.objects.get_or_create(
            name='Exclusions',
            trigger_type='keyword',
            defaults={
                'keywords': 'excluded, exclusion, exclusions, not covered, cosmetic, dental, overseas, abroad, travel, contraceptive',
                'response_message': 'Key exclusions: Cosmetic surgery, dental cosmetics/dentures, contraceptives, treatment abroad (unless Board-approved), non-accredited facilities (except emergencies). An agent can provide the full list.',
                'is_active': True,
                'priority': 75,
                'delay_seconds': 1,
            }
        )
        
        # Overseas treatment
        AutomatedResponse.objects.get_or_create(
            name='Overseas Treatment',
            trigger_type='keyword',
            defaults={
                'keywords': 'overseas, abroad, foreign, international, travel for treatment, treatment abroad, outside kenya',
                'response_message': 'Overseas treatment requires Board approval. Submit: 1st opinion (primary doctor), 2nd opinion (consultant), 3rd opinion (overseas hospital + costs) to DEFMIS Trustees. Processing: 1 month for stable cases, urgent cases expedited.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 1,
            }
        )
        
        # Emergency situations
        AutomatedResponse.objects.get_or_create(
            name='Emergency Help',
            trigger_type='keyword',
            defaults={
                'keywords': 'emergency, urgent, accident, acute, critical, serious, ambulance',
                'response_message': 'In emergencies: Seek immediate care at nearest facility. Hospital must notify DEFMIS within 24 hours. Ambulance costs require prior approval except in emergencies. For urgent help, call DEFMIS office.',
                'is_active': True,
                'priority': 90,
                'delay_seconds': 0,
            }
        )
        
        # Contact/Support
        AutomatedResponse.objects.get_or_create(
            name='Contact Information',
            trigger_type='keyword',
            defaults={
                'keywords': 'contact, call, phone, number, email, office, address, reach, talk to',
                'response_message': 'DEFMIS Contacts: Smart Access Support: 0203206000 / 0709326000. ICT Support: 0793531197 / 0793666333. Visit www.defmis.org for more information. An agent will assist you shortly.',
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
                'response_message': 'Thank you for contacting DEFMIS! Our office hours are Monday-Friday, 9 AM - 5 PM. Your message has been received and we will respond during business hours. For emergencies, seek immediate care and have the hospital notify us.',
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
                'response_message': 'All DEFMIS support agents are currently assisting other members. Your inquiry is important to us and will be answered as soon as possible. For urgent medical emergencies, please seek immediate care.',
                'is_active': True,
                'priority': 85,
                'delay_seconds': 2,
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default automated responses')
        )
