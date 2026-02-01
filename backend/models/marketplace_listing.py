from bson import ObjectId
from datetime import datetime, timedelta

class MarketplaceListing:
    """Model for marketplace credit listings"""
    
    def __init__(self, db):
        self.collection = db.marketplace_listings
    
    def create_listing(self, seller_id, credit_type, amount_kg_co2, price_per_kg):
        """
        Create a new marketplace listing
        
        Args:
            seller_id: User selling credits
            credit_type: Type of credit (solar/wind/bio)
            amount_kg_co2: Amount of credits to sell
            price_per_kg: Price per kg CO2
        
        Returns:
            Created listing document
        """
        listing = {
            'seller_id': seller_id,
            'credit_type': credit_type,
            'amount_kg_co2': float(amount_kg_co2),
            'original_amount': float(amount_kg_co2),
            'price_per_kg': float(price_per_kg),
            'total_price': float(amount_kg_co2 * price_per_kg),
            'status': 'active',
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=30),  # 30 day expiry
            'views': 0,
            'sold_amount': 0.0
        }
        
        result = self.collection.insert_one(listing)
        listing['_id'] = result.inserted_id
        
        return self._format_listing(listing)
    
    def get_active_listings(self, filters=None):
        """
        Get all active marketplace listings
        
        Args:
            filters: Optional filters (credit_type, max_price, min_amount)
        
        Returns:
            List of active listings
        """
        query = {
            'status': 'active',
            'amount_kg_co2': {'$gt': 0},
            'expires_at': {'$gt': datetime.utcnow()}
        }
        
        if filters:
            if 'credit_type' in filters:
                query['credit_type'] = filters['credit_type']
            if 'max_price' in filters:
                query['price_per_kg'] = {'$lte': float(filters['max_price'])}
            if 'min_amount' in filters:
                query['amount_kg_co2'] = {'$gte': float(filters['min_amount'])}
        
        listings = list(self.collection.find(query).sort('price_per_kg', 1))
        return [self._format_listing(l) for l in listings]
    
    def get_listing_by_id(self, listing_id):
        """Get a specific listing by ID"""
        listing = self.collection.find_one({'_id': ObjectId(listing_id)})
        return self._format_listing(listing) if listing else None
    
    def get_user_listings(self, user_id, status=None):
        """
        Get all listings created by a user
        
        Args:
            user_id: User ID
            status: Optional status filter (active/sold/cancelled)
        
        Returns:
            List of user's listings
        """
        query = {'seller_id': user_id}
        if status:
            query['status'] = status
        
        listings = list(self.collection.find(query).sort('created_at', -1))
        return [self._format_listing(l) for l in listings]
    
    def update_listing_amount(self, listing_id, amount_purchased):
        """
        Update listing after partial purchase
        
        Args:
            listing_id: Listing ID
            amount_purchased: Amount that was purchased
        """
        listing = self.collection.find_one({'_id': ObjectId(listing_id)})
        if not listing:
            raise ValueError('Listing not found')
        
        new_amount = listing['amount_kg_co2'] - amount_purchased
        sold_amount = listing.get('sold_amount', 0) + amount_purchased
        
        update = {
            'amount_kg_co2': new_amount,
            'sold_amount': sold_amount,
            'total_price': new_amount * listing['price_per_kg']
        }
        
        # Mark as sold if fully purchased
        if new_amount <= 0:
            update['status'] = 'sold'
            update['sold_at'] = datetime.utcnow()
        
        self.collection.update_one(
            {'_id': ObjectId(listing_id)},
            {'$set': update}
        )
        
        return self.get_listing_by_id(listing_id)
    
    def cancel_listing(self, listing_id, user_id):
        """
        Cancel a listing
        
        Args:
            listing_id: Listing ID
            user_id: User ID (must be seller)
        
        Returns:
            Updated listing
        """
        listing = self.collection.find_one({
            '_id': ObjectId(listing_id),
            'seller_id': user_id
        })
        
        if not listing:
            raise ValueError('Listing not found or unauthorized')
        
        if listing['status'] != 'active':
            raise ValueError('Can only cancel active listings')
        
        self.collection.update_one(
            {'_id': ObjectId(listing_id)},
            {'$set': {
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow()
            }}
        )
        
        return self.get_listing_by_id(listing_id)
    
    def increment_views(self, listing_id):
        """Increment view count for a listing"""
        self.collection.update_one(
            {'_id': ObjectId(listing_id)},
            {'$inc': {'views': 1}}
        )
    
    def _format_listing(self, listing):
        """Format listing for API response"""
        if not listing:
            return None
        
        return {
            'listing_id': str(listing['_id']),
            'seller_id': listing['seller_id'],
            'credit_type': listing['credit_type'],
            'amount_kg_co2': listing['amount_kg_co2'],
            'original_amount': listing.get('original_amount', listing['amount_kg_co2']),
            'price_per_kg': listing['price_per_kg'],
            'total_price': listing['total_price'],
            'status': listing['status'],
            'created_at': listing['created_at'].isoformat(),
            'expires_at': listing['expires_at'].isoformat(),
            'views': listing.get('views', 0),
            'sold_amount': listing.get('sold_amount', 0.0),
            'sold_at': listing.get('sold_at').isoformat() if listing.get('sold_at') else None,
            'cancelled_at': listing.get('cancelled_at').isoformat() if listing.get('cancelled_at') else None
        }
