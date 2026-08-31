from django.conf import settings

def bank_details(request):
    """
    Global context processor providing official settlement bank account details to templates.
    """
    return {
        'BANK_NAME': getattr(settings, 'PAYSTACK_BANK_NAME', 'OPay'),
        'ACCOUNT_NUMBER': getattr(settings, 'PAYSTACK_ACCOUNT_NUMBER', '8148281423'),
        'ACCOUNT_NAME': getattr(settings, 'PAYSTACK_ACCOUNT_NAME', 'Lukexx Business And Technology'),
    }
