import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from payments.services import PaystackService

def test_live_paystack_api():
    print(f"Testing Paystack Secret Key: {PaystackService.get_headers()}")
    res = PaystackService.initialize_transaction(
        email="clienttest@example.com",
        amount_kobo=10000, # 100.00 NGN
        reference="BBS-TEST-KEY-INIT-1",
        callback_url="http://127.0.0.1:8000/payments/verify/?payment_ref=BBS-TEST-KEY-INIT-1"
    )
    print("Paystack API Response:", res)
    if res.get('status') and 'checkout.paystack.com' in res.get('data', {}).get('authorization_url', ''):
        print(" SUCCESS! Real Paystack authorization_url generated:", res['data']['authorization_url'])
    else:
        print(" Failed to initialize real Paystack transaction:", res)

if __name__ == '__main__':
    test_live_paystack_api()
