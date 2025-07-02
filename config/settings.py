"""
Centralized configuration for Jasmin Catering AI Agent
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Azure Configuration
AZURE_CONFIG = {
    'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
    'resource_group': os.getenv('AZURE_RESOURCE_GROUP', 'logicapp-jasmin-sweden_group'),
    'location': os.getenv('AZURE_LOCATION', 'swedencentral'),
    'key_vault_name': os.getenv('AZURE_KEY_VAULT_NAME', 'jasmin-catering-kv'),
    'key_vault_uri': os.getenv('AZURE_KEY_VAULT_URI'),
}

# AI Services Configuration
AI_CONFIG = {
    'endpoint': os.getenv('AZURE_AI_ENDPOINT', 'https://swedencentral.api.cognitive.microsoft.com'),
    'api_key': os.getenv('AZURE_AI_API_KEY'),
    'deployment_name': 'gpt-4o',
    'temperature': 0.3,
    'max_tokens': 2500,
}

# Azure Search Configuration
SEARCH_CONFIG = {
    'endpoint': 'https://jasmin-catering-search.search.windows.net',
    'api_key': os.getenv('AZURE_SEARCH_API_KEY'),
    'index_name': 'jasmin-catering-knowledge',
}

# Email Configuration
EMAIL_CONFIG = {
    'imap_server': 'imap.web.de',
    'imap_port': 993,
    'smtp_server': 'smtp.web.de',
    'smtp_port': 587,
    'address': os.getenv('FROM_EMAIL_ADDRESS', 'matthias.buchhorn@web.de'),
    'password': os.getenv('WEBDE_APP_PASSWORD'),
    'alias': os.getenv('WEBDE_EMAIL_ALIAS', 'ma3u-test@email.de'),
}

# Slack Configuration
SLACK_CONFIG = {
    'bot_token': os.getenv('SLACK_BOT_TOKEN'),
    'email_channel_id': os.getenv('SLACK_CHANNEL_ID'),
    'log_channel_id': os.getenv('SLACK_LOG_CHANNEL_ID'),
    'app_id': os.getenv('SLACK_APP_ID'),
}

# Business Configuration
BUSINESS_CONFIG = {
    'name': 'Jasmin Catering',
    'location': 'Berlin, Deutschland',
    'service_area': 'Berlin und Umgebung (bis 50km)',
    'min_order': 10,
    'advance_notice': 48,  # hours
    'packages': {
        'basis': {'price_range': (25, 35), 'name': 'Basis-Paket'},
        'standard': {'price_range': (35, 45), 'name': 'Standard-Paket'},
        'premium': {'price_range': (50, 70), 'name': 'Premium-Paket'},
    },
    'discounts': {
        'weekday': 0.10,  # 10% Mon-Thu
        'large_group': 0.10,  # 10% for 50+ people
        'nonprofit': 0.10,  # 10% for nonprofits
        'loyalty': 0.05,  # 5% after 3 bookings
    },
    'surcharges': {
        'weekend': 0.10,  # 10%
        'rush': 0.25,  # 25% for <48h
        'holiday': 0.20,  # 20%
        'summer': 0.15,  # 15% May-October
    },
}