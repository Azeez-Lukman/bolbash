import hmac
import hashlib
import json
import urllib.request
import urllib.parse
from django.conf import settings


class PaystackService:
    """
    Dedicated service helper for communicating with Paystack API server-side.
    Secret keys remain strictly on the server and are never exposed to the client.
    """

    @classmethod
    def get_headers(cls):
        return {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

    @classmethod
    def initialize_transaction(cls, email, amount_kobo, reference, callback_url, metadata=None):
        """
        Initializes a Paystack payment transaction.
        Amount must be in Kobo (e.g., ₦10,000 = 1,000,000 Kobo).
        """
        url = f"{settings.PAYSTACK_PAYMENT_URL}/transaction/initialize"
        
        payload = {
            'email': email,
            'amount': amount_kobo,
            'reference': reference,
            'callback_url': callback_url,
            'currency': 'NGN',
        }
        if metadata:
            payload['metadata'] = metadata

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=cls.get_headers(), method='POST')

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data
        except Exception as e:
            # When in test mode without real API key, return mock data for local testing
            if 'placeholder' in settings.PAYSTACK_SECRET_KEY:
                return {
                    'status': True,
                    'message': 'Mock Paystack Authorization (Development Mode)',
                    'data': {
                        'authorization_url': f"{callback_url}?trxref={reference}&reference={reference}",
                        'access_code': 'mock_access_code_dev',
                        'reference': reference
                    }
                }
            raise e

    @classmethod
    def verify_transaction(cls, paystack_reference):
        """
        Independently verifies a Paystack transaction status with Paystack API.
        """
        encoded_ref = urllib.parse.quote(paystack_reference)
        url = f"{settings.PAYSTACK_PAYMENT_URL}/transaction/verify/{encoded_ref}"

        req = urllib.request.Request(url, headers=cls.get_headers(), method='GET')

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data
        except Exception as e:
            # When in test mode without real API key, return mock verified response
            if 'placeholder' in settings.PAYSTACK_SECRET_KEY:
                return {
                    'status': True,
                    'message': 'Verification successful (Development Mock)',
                    'data': {
                        'status': 'success',
                        'reference': paystack_reference,
                        'amount': None,  # Will be verified against server expected
                        'currency': 'NGN',
                        'gateway_response': 'Successful Mock Test Payment',
                        'channel': 'card'
                    }
                }
            raise e

    @classmethod
    def verify_webhook_signature(cls, payload_bytes, signature_header):
        """
        Validates Paystack HMAC-SHA512 webhook signature header against secret key.
        """
        if not signature_header or not settings.PAYSTACK_SECRET_KEY:
            return False

        secret_bytes = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_hash = hmac.new(secret_bytes, payload_bytes, hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed_hash, signature_header)
