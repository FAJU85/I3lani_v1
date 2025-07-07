"""
Initialize default packages in database
"""
import asyncio
from database import Database

async def init_default_packages():
    """Initialize default packages in database"""
    db = Database()
    
    # Initialize database first
    await db.init_db()
    
    # Check if packages already exist
    existing_packages = await db.get_packages(active_only=False)
    if existing_packages:
        print("Packages already initialized")
        return
    
    # Default packages
    default_packages = [
        {
            'package_id': 'bronze',
            'name': 'Bronze Plan',
            'price_usd': 10.0,
            'duration_days': 30,
            'posts_per_day': 1,
            'channels_included': 1
        },
        {
            'package_id': 'silver',
            'name': 'Silver Plan',
            'price_usd': 29.0,
            'duration_days': 90,
            'posts_per_day': 3,
            'channels_included': 3
        },
        {
            'package_id': 'gold',
            'name': 'Gold Plan',
            'price_usd': 47.0,
            'duration_days': 180,
            'posts_per_day': 6,
            'channels_included': 5
        }
    ]
    
    # Create packages
    for package in default_packages:
        await db.create_package(
            package['package_id'],
            package['name'],
            package['price_usd'],
            package['duration_days'],
            package['posts_per_day'],
            package['channels_included']
        )
        print(f"✅ Created package: {package['name']}")
    
    print("🎯 Default packages initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_default_packages())