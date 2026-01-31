#!/usr/bin/env python3
"""
Comprehensive MongoDB Status Report
"""

from pymongo import MongoClient
from config import Config
from datetime import datetime

def generate_status_report():
    """Generate detailed MongoDB status report"""
    
    print("\n" + "=" * 70)
    print("📊 MONGODB CONNECTION STATUS REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_database()
        
        # Connection Status
        print("\n✅ CONNECTION STATUS: ACTIVE")
        print("-" * 70)
        print(f"   Database Name: {db.name}")
        print(f"   Server Address: {client.address[0]}:{client.address[1]}")
        print(f"   MongoDB Version: {client.server_info().get('version', 'Unknown')}")
        
        # Collections Overview
        collections = db.list_collection_names()
        print(f"\n📚 COLLECTIONS ({len(collections)} total)")
        print("-" * 70)
        
        if collections:
            for col_name in sorted(collections):
                collection = db[col_name]
                count = collection.count_documents({})
                
                print(f"\n   📁 {col_name.upper()}")
                print(f"      Documents: {count}")
                
                # Show sample document structure if available
                if count > 0:
                    sample = collection.find_one()
                    if sample:
                        fields = list(sample.keys())
                        print(f"      Fields: {', '.join(fields[:10])}")
                        if len(fields) > 10:
                            print(f"              ... and {len(fields) - 10} more")
        else:
            print("   (No collections created yet)")
        
        # Database Statistics
        stats = db.command("dbStats")
        print(f"\n💾 DATABASE STATISTICS")
        print("-" * 70)
        print(f"   Storage Size: {stats.get('storageSize', 0) / 1024:.2f} KB")
        print(f"   Data Size: {stats.get('dataSize', 0) / 1024:.2f} KB")
        print(f"   Index Size: {stats.get('indexSize', 0) / 1024:.2f} KB")
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Indexes: {stats.get('indexes', 0)}")
        
        # Configuration
        print(f"\n⚙️  CONFIGURATION")
        print("-" * 70)
        print(f"   MongoDB URI: {Config.MONGO_URI}")
        print(f"   Emission Factor (kWh): {Config.EMISSION_FACTOR_KWH} kg CO2/kWh")
        print(f"   Carbon Limit (Base): {Config.CARBON_LIMIT_BASE_PER_SQM} kg CO2/m²/year")
        print(f"   Carbon Limit (Per Person): {Config.CARBON_LIMIT_PER_OCCUPANT} kg CO2/year")
        
        # Credit Types
        print(f"\n💰 AVAILABLE CREDIT TYPES")
        print("-" * 70)
        for credit_type, details in Config.CREDIT_TYPES.items():
            print(f"   {details['icon']} {details['name']}")
            print(f"      Type: {credit_type}")
            print(f"      Price: ${details['price_per_kg']:.2f} per kg CO2")
            print(f"      Description: {details['description']}")
        
        print("\n" + "=" * 70)
        print("✅ MONGODB IS FULLY OPERATIONAL")
        print("=" * 70)
        print("\n💡 Next Steps:")
        print("   - Backend API is ready to accept requests")
        print("   - Start backend: python app.py")
        print("   - Access API: http://localhost:5000")
        print("   - Health check: http://localhost:5000/api/health")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("=" * 70)
        print("\n")

if __name__ == "__main__":
    generate_status_report()
