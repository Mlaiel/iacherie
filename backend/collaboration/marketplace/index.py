"""Index Module - Marketplace System Entry Point
============================================

Centralized entry point for the complete marketplace system providing
quick access to all marketplace components and utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from . import (
    BiddingSystem,
    AuctionEngine,
    EscrowManager,
    RatingSystem,
    DisputeResolver,
    MarketAnalyzer,
    PriceOptimizer,
    ServiceCatalog,
    PortfolioManager,
    CommissionCalculator,
    PerformanceTracker
)

def get_marketplace_engine(config=None):
    """Get unified marketplace engine with all components"""
    return {
        'bidding_system': BiddingSystem(config),
        'auction_engine': AuctionEngine(config),
        'escrow_manager': EscrowManager(config),
        'rating_system': RatingSystem(config),
        'dispute_resolver': DisputeResolver(config),
        'market_analyzer': MarketAnalyzer(config),
        'price_optimizer': PriceOptimizer(config),
        'service_catalog': ServiceCatalog(config),
        'portfolio_manager': PortfolioManager(config),
        'commission_calculator': CommissionCalculator(config),
        'performance_tracker': PerformanceTracker(config)
    }

async def process_complete_transaction(
    service_request: dict,
    buyer_profile: dict,
    seller_profile: dict,
    marketplace_config: dict = None
):
    """Process complete marketplace transaction from bidding to completion"""
    engine = get_marketplace_engine(marketplace_config)
    
    results = {}
    
    # Step 1: Create auction/bidding
    auction = await engine['auction_engine'].create_auction(
        service_request, seller_profile
    )
    results['auction'] = auction
    
    # Step 2: Process bids
    bidding_results = await engine['bidding_system'].process_bids(
        auction['auction_id'], [buyer_profile]
    )
    results['bidding'] = bidding_results
    
    # Step 3: Set up escrow
    if bidding_results['winning_bid']:
        escrow = await engine['escrow_manager'].create_escrow(
            bidding_results['winning_bid'], service_request
        )
        results['escrow'] = escrow
    
    # Step 4: Calculate commissions
    commission = await engine['commission_calculator'].calculate_fees(
        bidding_results['winning_bid']
    )
    results['commission'] = commission
    
    return results

async def get_marketplace_analytics(creator_id: str, marketplace_engine=None):
    """Get comprehensive marketplace analytics for a creator"""
    if not marketplace_engine:
        marketplace_engine = get_marketplace_engine()
    
    analytics = {}
    
    # Performance metrics
    performance = await marketplace_engine['performance_tracker'].get_creator_metrics(creator_id)
    analytics['performance'] = performance
    
    # Market analysis
    market_insights = await marketplace_engine['market_analyzer'].analyze_creator_market(creator_id)
    analytics['market_insights'] = market_insights
    
    # Portfolio analytics
    portfolio_stats = await marketplace_engine['portfolio_manager'].get_portfolio_analytics(creator_id)
    analytics['portfolio'] = portfolio_stats
    
    # Rating summary
    rating_summary = await marketplace_engine['rating_system'].get_creator_rating_summary(creator_id)
    analytics['ratings'] = rating_summary
    
    return analytics