'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, DollarSign, CreditCard, TrendingUp, Package, ShoppingCart, Award, Loader2, Check, Zap } from 'lucide-react';

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  billing_period: 'monthly' | 'yearly';
  features: string[];
  limits: {
    content_generations: number;
    ai_credits: number;
    storage_gb: number;
    collaborators: number;
  };
  is_popular: boolean;
  stripe_price_id?: string;
}

interface Subscription {
  id: string;
  user_id: string;
  plan_id: string;
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

interface PaymentMethod {
  id: string;
  type: 'card' | 'paypal' | 'crypto';
  last4?: string;
  brand?: string;
  exp_month?: number;
  exp_year?: number;
}

export default function MonetizationPage() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');
  
  // Revenue Stats
  const [revenueStats, setRevenueStats] = useState({
    total_revenue: 0,
    monthly_recurring: 0,
    active_subscriptions: 0,
    conversion_rate: 0,
  });

  useEffect(() => {
    fetchData();
  }, [billingPeriod]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch pricing plans
      const plansResponse = await fetch('http://localhost:8000/monetization/plans');
      if (plansResponse.ok) {
        const plansData = await plansResponse.json();
        setPlans(plansData.plans || []);
      }

      // Fetch current subscription
      const subResponse = await fetch('http://localhost:8000/monetization/subscription', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (subResponse.ok) {
        const subData = await subResponse.json();
        setSubscription(subData.subscription);
      }

      // Fetch payment methods
      const paymentResponse = await fetch('http://localhost:8000/monetization/payment-methods', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (paymentResponse.ok) {
        const paymentData = await paymentResponse.json();
        setPaymentMethods(paymentData.payment_methods || []);
      }

      // Fetch revenue stats
      const statsResponse = await fetch('http://localhost:8000/monetization/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setRevenueStats(statsData.stats || revenueStats);
      }
    } catch (error) {
      console.error('Error fetching monetization data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (planId: string) => {
    try {
      setCheckoutLoading(planId);

      const response = await fetch('http://localhost:8000/monetization/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          plan_id: planId,
          billing_period: billingPeriod,
          success_url: `${window.location.origin}/monetization/success`,
          cancel_url: `${window.location.origin}/monetization`,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Redirect to Stripe Checkout
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } else {
        alert('Failed to create checkout session');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Error creating checkout session');
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handleCancelSubscription = async () => {
    if (!subscription || !confirm('Are you sure you want to cancel your subscription?')) return;

    try {
      const response = await fetch('http://localhost:8000/monetization/subscription/cancel', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        alert('Subscription canceled successfully');
        fetchData();
      } else {
        alert('Failed to cancel subscription');
      }
    } catch (error) {
      console.error('Cancel subscription error:', error);
    }
  };

  const filteredPlans = plans.filter(plan => plan.billing_period === billingPeriod);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-green-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Monetization Hub</h1>
                <p className="text-sm text-gray-500">Pricing • Billing • Revenue Management</p>
              </div>
            </div>
            {subscription && (
              <div className="flex items-center space-x-2 bg-green-100 text-green-700 px-4 py-2 rounded-lg">
                <Award className="h-5 w-5" />
                <span className="font-semibold">Active Subscription</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Revenue Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <span className="text-xs text-gray-500">Total</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              ${revenueStats.total_revenue.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Revenue</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Package className="h-8 w-8 text-blue-600" />
              <span className="text-xs text-gray-500">MRR</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              ${revenueStats.monthly_recurring.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Monthly Recurring</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Award className="h-8 w-8 text-purple-600" />
              <span className="text-xs text-gray-500">Active</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {revenueStats.active_subscriptions}
            </div>
            <div className="text-sm text-gray-600">Subscriptions</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <Zap className="h-8 w-8 text-orange-600" />
              <span className="text-xs text-gray-500">Rate</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {revenueStats.conversion_rate}%
            </div>
            <div className="text-sm text-gray-600">Conversion Rate</div>
          </div>
        </div>

        {/* Current Subscription */}
        {subscription && (
          <div className="bg-gradient-to-r from-green-500 to-blue-500 rounded-xl shadow-lg p-6 mb-8 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold mb-2">Your Current Plan</h3>
                <p className="opacity-90">
                  Active until {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={handleCancelSubscription}
                className="bg-white text-red-600 px-6 py-2 rounded-lg font-semibold hover:bg-red-50 transition"
              >
                Cancel Subscription
              </button>
            </div>
          </div>
        )}

        {/* Billing Period Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-xl shadow-lg p-2 inline-flex">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`px-8 py-3 rounded-lg font-semibold transition ${
                billingPeriod === 'monthly'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`px-8 py-3 rounded-lg font-semibold transition relative ${
                billingPeriod === 'yearly'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Yearly
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Plans */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-green-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {filteredPlans.map((plan) => (
              <div
                key={plan.id}
                className={`bg-white rounded-xl shadow-xl p-8 relative transform transition hover:scale-105 ${
                  plan.is_popular ? 'ring-4 ring-green-500' : ''
                }`}
              >
                {plan.is_popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-green-500 text-white px-6 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center mb-4">
                    <span className="text-5xl font-bold text-gray-900">${plan.price}</span>
                    <span className="text-gray-600 ml-2">/{billingPeriod === 'monthly' ? 'mo' : 'yr'}</span>
                  </div>
                </div>

                {/* Limits */}
                <div className="space-y-3 mb-8">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Content Generations</span>
                    <span className="font-semibold text-gray-900">
                      {plan.limits.content_generations === -1 ? 'Unlimited' : plan.limits.content_generations}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">AI Credits</span>
                    <span className="font-semibold text-gray-900">
                      {plan.limits.ai_credits === -1 ? 'Unlimited' : plan.limits.ai_credits}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Storage</span>
                    <span className="font-semibold text-gray-900">{plan.limits.storage_gb}GB</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Collaborators</span>
                    <span className="font-semibold text-gray-900">
                      {plan.limits.collaborators === -1 ? 'Unlimited' : plan.limits.collaborators}
                    </span>
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start text-sm text-gray-700">
                      <Check className="h-5 w-5 text-green-600 mr-2 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <button
                  onClick={() => handleCheckout(plan.id)}
                  disabled={checkoutLoading === plan.id || (subscription?.plan_id === plan.id)}
                  className={`w-full py-4 px-6 rounded-lg font-semibold transition-all ${
                    plan.is_popular
                      ? 'bg-gradient-to-r from-green-600 to-blue-600 text-white hover:from-green-700 hover:to-blue-700'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  } disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2`}
                >
                  {checkoutLoading === plan.id ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : subscription?.plan_id === plan.id ? (
                    <>
                      <Check className="h-5 w-5" />
                      <span>Current Plan</span>
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="h-5 w-5" />
                      <span>Subscribe Now</span>
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Payment Methods */}
        {paymentMethods.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Payment Methods</h3>
              <button className="text-green-600 hover:text-green-700 font-semibold">
                + Add New
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {paymentMethods.map((method) => (
                <div key={method.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <CreditCard className="h-8 w-8 text-gray-600" />
                    <span className="text-xs text-gray-500">{method.type}</span>
                  </div>
                  {method.type === 'card' && (
                    <>
                      <div className="font-semibold text-gray-900">
                        {method.brand} •••• {method.last4}
                      </div>
                      <div className="text-sm text-gray-600">
                        Expires {method.exp_month}/{method.exp_year}
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
