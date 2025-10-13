/**
 * @fileoverview Monetization-related enumerations
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

export enum RevenueType {
  SUBSCRIPTION = 'subscription',
  ONE_TIME_PURCHASE = 'one_time_purchase',
  LICENSING = 'licensing',
  ADVERTISING = 'advertising',
  COMMISSION = 'commission',
  ROYALTY = 'royalty',
}

export enum PricingModel {
  FREE = 'free',
  FIXED_PRICE = 'fixed_price',
  TIERED_PRICING = 'tiered_pricing',
  PAY_PER_USE = 'pay_per_use',
  SUBSCRIPTION = 'subscription',
  AUCTION = 'auction',
  NAME_YOUR_PRICE = 'name_your_price',
}

export enum Currency {
  USD = 'USD',
  EUR = 'EUR',
  GBP = 'GBP',
  JPY = 'JPY',
  CAD = 'CAD',
  AUD = 'AUD',
  CHF = 'CHF',
  CNY = 'CNY',
}

export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
  DISPUTED = 'disputed',
  CANCELLED = 'cancelled',
}

export enum PaymentMethod {
  CREDIT_CARD = 'credit_card',
  DEBIT_CARD = 'debit_card',
  PAYPAL = 'paypal',
  STRIPE = 'stripe',
  BANK_TRANSFER = 'bank_transfer',
  CRYPTOCURRENCY = 'cryptocurrency',
  APPLE_PAY = 'apple_pay',
  GOOGLE_PAY = 'google_pay',
}

export enum LicenseType {
  STANDARD = 'standard',
  EXTENDED = 'extended',
  EXCLUSIVE = 'exclusive',
  ROYALTY_FREE = 'royalty_free',
  RIGHTS_MANAGED = 'rights_managed',
  CREATIVE_COMMONS = 'creative_commons',
  PUBLIC_DOMAIN = 'public_domain',
}

export enum SubscriptionBilling {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  YEARLY = 'yearly',
  LIFETIME = 'lifetime',
}

export enum MarketplaceCategory {
  STOCK_MEDIA = 'stock_media',
  TEMPLATES = 'templates',
  MUSIC_LOOPS = 'music_loops',
  SOUND_EFFECTS = 'sound_effects',
  FONTS = 'fonts',
  GRAPHICS = 'graphics',
  PRESETS = 'presets',
  COURSES = 'courses',
}