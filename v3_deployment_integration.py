
# Add V3 system initialization to deployment
from v3_integration_main import initialize_i3lani_v3

async def initialize_v3_in_deployment(bot, dp):
    """Initialize V3 system in deployment"""
    await initialize_i3lani_v3(bot, dp)
