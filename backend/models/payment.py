from bson import ObjectId
from datetime import datetime
import secrets

class Payment:
    """Model for payment transactions"""
    
    def __init__(self, db):
        self.collection = db.payments
    
    def create_payment(self, buyer_id, listing_id, amount_kg_co2, total_amount, payment_method):
        """
        Create a new payment transaction
        
        Args:
            buyer_id: User making the purchase
            listing_id: Marketplace listing ID
            amount_kg_co2: Amount of credits being purchased
            total_amount: Total payment amount
            payment_method: Payment method (upi/qr/card)
        
        Returns:
            Payment document with transaction ID
        """
        transaction_id = f"TXN{secrets.token_hex(8).upper()}"
        
        payment = {
            'transaction_id': transaction_id,
            'buyer_id': buyer_id,
            'listing_id': listing_id,
            'amount_kg_co2': float(amount_kg_co2),
            'total_amount': float(total_amount),
            'payment_method': payment_method,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'upi_id': None,
            'qr_code': None,
            'payment_link': None
        }
        
        result = self.collection.insert_one(payment)
        payment['_id'] = result.inserted_id
        
        return self._format_payment(payment)
    
    def get_payment_by_id(self, payment_id):
        """Get payment by ID"""
        payment = self.collection.find_one({'_id': ObjectId(payment_id)})
        return self._format_payment(payment) if payment else None
    
    def get_payment_by_transaction_id(self, transaction_id):
        """Get payment by transaction ID"""
        payment = self.collection.find_one({'transaction_id': transaction_id})
        return self._format_payment(payment) if payment else None
    
    def update_payment_status(self, payment_id, status, payment_details=None):
        """
        Update payment status
        
        Args:
            payment_id: Payment ID
            status: New status (pending/completed/failed/cancelled)
            payment_details: Optional payment details (UPI ref, etc.)
        
        Returns:
            Updated payment
        """
        update = {'status': status}
        
        if status == 'completed':
            update['completed_at'] = datetime.utcnow()
        elif status == 'failed':
            update['failed_at'] = datetime.utcnow()
        
        if payment_details:
            update.update(payment_details)
        
        self.collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': update}
        )
        
        return self.get_payment_by_id(payment_id)
    
    def get_user_payments(self, user_id, status=None):
        """Get all payments by a user"""
        query = {'buyer_id': user_id}
        if status:
            query['status'] = status
        
        payments = list(self.collection.find(query).sort('created_at', -1))
        return [self._format_payment(p) for p in payments]
    
    def add_payment_details(self, payment_id, upi_id=None, qr_code=None, payment_link=None):
        """Add payment details (UPI ID, QR code, etc.)"""
        update = {}
        if upi_id:
            update['upi_id'] = upi_id
        if qr_code:
            update['qr_code'] = qr_code
        if payment_link:
            update['payment_link'] = payment_link
        
        if update:
            self.collection.update_one(
                {'_id': ObjectId(payment_id)},
                {'$set': update}
            )
        
        return self.get_payment_by_id(payment_id)
    
    def get_all_payments(self, limit=50, offset=0):
        """
        Get all payments (for admin)
        """
        payments = list(self.collection.find()
                       .sort('created_at', -1)
                       .skip(offset)
                       .limit(limit))
        return [self._format_payment(p) for p in payments]

    def _format_payment(self, payment):
        """Format payment for API response"""
        if not payment:
            return None
        
        return {
            'payment_id': str(payment['_id']),
            'transaction_id': payment['transaction_id'],
            'buyer_id': payment['buyer_id'],
            'listing_id': payment['listing_id'],
            'amount_kg_co2': payment['amount_kg_co2'],
            'total_amount': payment['total_amount'],
            'payment_method': payment['payment_method'],
            'status': payment['status'],
            'created_at': payment['created_at'].isoformat(),
            'completed_at': payment.get('completed_at').isoformat() if payment.get('completed_at') else None,
            'failed_at': payment.get('failed_at').isoformat() if payment.get('failed_at') else None,
            'upi_id': payment.get('upi_id'),
            'qr_code': payment.get('qr_code'),
            'payment_link': payment.get('payment_link')
        }
