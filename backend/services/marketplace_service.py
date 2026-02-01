from models.marketplace_listing import MarketplaceListing
from models.credit import Credit
from models.payment import Payment
from models.user import User
import qrcode
import io
import base64

class MarketplaceService:
    """Service for marketplace trading operations"""
    
    def __init__(self, db):
        self.db = db
        self.marketplace_model = MarketplaceListing(db)
        self.credit_model = Credit(db)
        self.payment_model = Payment(db)
        self.user_model = User(db)
    
    def create_sell_listing(self, seller_id, credit_type, amount_kg_co2, price_per_kg):
        """
        Create a new sell listing
        
        Validates that seller has enough credits to sell
        """
        # Check if user has enough credits
        user_credits = self.credit_model.get_credit_summary(seller_id)
        available = user_credits.get('total_offset_kg', 0)
        
        if available < amount_kg_co2:
            raise ValueError(f'Insufficient credits. Available: {available} kg, Requested: {amount_kg_co2} kg')
            
        if price_per_kg < 5:
            raise ValueError('Minimum price per kg must be at least 5 Rs')
        
        # Create listing
        listing = self.marketplace_model.create_listing(
            seller_id, credit_type, amount_kg_co2, price_per_kg
        )
        
        # Mark credits as "locked" for this listing
        # (In a real system, you'd create a separate "locked_credits" collection)
        
        return listing
    
    def get_marketplace_listings(self, filters=None):
        """Get all active marketplace listings"""
        return self.marketplace_model.get_active_listings(filters)
    
    def get_listing_details(self, listing_id):
        """Get detailed information about a listing"""
        listing = self.marketplace_model.get_listing_by_id(listing_id)
        if not listing:
            raise ValueError('Listing not found')
        
        # Increment view count
        self.marketplace_model.increment_views(listing_id)
        
        # Get seller info (anonymized)
        seller = self.user_model.get_user_by_id(listing['seller_id'])
        if seller:
            listing['seller_email'] = seller['email'][:3] + '***@' + seller['email'].split('@')[1]
        
        return listing
    
    def initiate_purchase(self, buyer_id, listing_id, amount_kg_co2, payment_method):
        """
        Initiate a purchase from marketplace
        
        Args:
            buyer_id: User buying credits
            listing_id: Listing to buy from
            amount_kg_co2: Amount to purchase
            payment_method: Payment method (upi/qr/card)
        
        Returns:
            Payment details with QR code/UPI ID
        """
        # Get listing
        listing = self.marketplace_model.get_listing_by_id(listing_id)
        if not listing:
            raise ValueError('Listing not found')
        
        if listing['status'] != 'active':
            raise ValueError('Listing is not active')
        
        if listing['seller_id'] == buyer_id:
            raise ValueError('Cannot buy from your own listing')
        
        if amount_kg_co2 > listing['amount_kg_co2']:
            raise ValueError(f'Insufficient amount available. Available: {listing["amount_kg_co2"]} kg')
        
        # Calculate total amount
        total_amount = amount_kg_co2 * listing['price_per_kg']
        
        # Create payment
        payment = self.payment_model.create_payment(
            buyer_id, listing_id, amount_kg_co2, total_amount, payment_method
        )
        
        # Generate payment details based on method
        if payment_method == 'upi':
            upi_id = self._generate_upi_id(listing['seller_id'])
            qr_code = self._generate_upi_qr(upi_id, total_amount, payment['transaction_id'])
            
            payment = self.payment_model.add_payment_details(
                payment['payment_id'],
                upi_id=upi_id,
                qr_code=qr_code
            )
        elif payment_method == 'qr':
            qr_code = self._generate_payment_qr(total_amount, payment['transaction_id'])
            payment = self.payment_model.add_payment_details(
                payment['payment_id'],
                qr_code=qr_code
            )
        
        return payment
    
    def complete_purchase(self, payment_id, payment_reference=None):
        """
        Complete a purchase after payment verification
        
        In a real system, this would be called by a payment webhook
        """
        payment = self.payment_model.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError('Payment not found')
        
        if payment['status'] != 'pending':
            raise ValueError(f'Payment already {payment["status"]}')
        
        # Get listing
        listing = self.marketplace_model.get_listing_by_id(payment['listing_id'])
        if not listing:
            raise ValueError('Listing not found')
        
        # Transfer credits from seller to buyer
        self._transfer_credits(
            listing['seller_id'],
            payment['buyer_id'],
            listing['credit_type'],
            payment['amount_kg_co2']
        )
        
        # Update listing amount
        self.marketplace_model.update_listing_amount(
            payment['listing_id'],
            payment['amount_kg_co2']
        )
        
        # Increase buyer's carbon limit
        self.user_model.increase_carbon_limit(
            payment['buyer_id'], 
            payment['amount_kg_co2']
        )
        
        # Update payment status
        payment_details = {}
        if payment_reference:
            payment_details['payment_reference'] = payment_reference
        
        payment = self.payment_model.update_payment_status(
            payment_id, 'completed', payment_details
        )
        
        return {
            'success': True,
            'message': 'Purchase completed successfully',
            'payment': payment,
            'credits_received': payment['amount_kg_co2']
        }
    
    def cancel_listing(self, listing_id, user_id):
        """Cancel a user's listing"""
        return self.marketplace_model.cancel_listing(listing_id, user_id)
    
    def get_user_listings(self, user_id):
        """Get all listings created by a user"""
        return self.marketplace_model.get_user_listings(user_id)
    
    def get_user_trades(self, user_id):
        """Get user's trading history (buys and sells)"""
        # Get sell listings
        sell_listings = self.marketplace_model.get_user_listings(user_id)
        
        # Get purchase payments
        purchases = self.payment_model.get_user_payments(user_id, status='completed')
        
        return {
            'sell_listings': sell_listings,
            'purchases': purchases
        }
    
    def _transfer_credits(self, from_user_id, to_user_id, credit_type, amount_kg_co2):
        """Transfer credits between users"""
        # In a real system, this would:
        # 1. Deduct from seller's credits
        # 2. Add to buyer's credits
        # For now, we'll just add to buyer
        
        from config import Config
        credit_info = Config.CREDIT_TYPES.get(credit_type, {})
        
        self.credit_model.deduct_credits(from_user_id, amount_kg_co2)
        
        self.credit_model.purchase_credit(
            to_user_id,
            credit_type,
            amount_kg_co2,
            amount_kg_co2 * credit_info.get('price_per_kg', 0.15)
        )
    
    def _generate_upi_id(self, seller_id):
        """Generate UPI ID for seller (simulated)"""
        # In a real system, this would be the seller's actual UPI ID
        return f"seller{seller_id[:8]}@upi"
    
    def _generate_upi_qr(self, upi_id, amount, transaction_id):
        """Generate UPI QR code"""
        # UPI payment string format
        upi_string = f"upi://pay?pa={upi_id}&pn=CarbonCredit&am={amount}&tn={transaction_id}&cu=INR"
        
        return self._generate_qr_code(upi_string)
    
    def _generate_payment_qr(self, amount, transaction_id):
        """Generate generic payment QR code"""
        payment_string = f"PAYMENT|TXN:{transaction_id}|AMT:{amount}|CUR:INR"
        return self._generate_qr_code(payment_string)
    
    def _generate_qr_code(self, data):
        """Generate QR code and return as base64 image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
