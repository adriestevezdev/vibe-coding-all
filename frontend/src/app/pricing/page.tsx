'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import api, { Product, UserPremiumStatus } from '../../../services/api';

export default function PricingPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [premiumStatus, setPremiumStatus] = useState<UserPremiumStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      loadData();
    }
  }, [user, isLoading, router]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [productsResponse, statusResponse] = await Promise.all([
        api.payments.getProducts(),
        api.payments.getUserPremiumStatus(),
      ]);
      
      setProducts(productsResponse.products);
      setPremiumStatus(statusResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load pricing data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (productId: string) => {
    try {
      setPurchasing(true);
      setError(null);

      const checkoutResponse = await api.payments.createCheckoutSession({
        product_id: productId,
        success_url: `${window.location.origin}/payments/success`,
        metadata: {
          user_id: user?.id,
          product_type: 'premium',
        },
      });

      // Redirect to Polar checkout
      window.location.href = checkoutResponse.checkout_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create checkout session');
      setPurchasing(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Choose Your Plan
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Unlock the full potential of VibeCoding with premium features
          </p>
        </div>

        {/* Current Status */}
        {premiumStatus && (
          <div className="mt-8 max-w-md mx-auto">
            <div className={`p-4 rounded-lg border ${
              premiumStatus.is_premium 
                ? 'bg-green-50 border-green-200' 
                : 'bg-yellow-50 border-yellow-200'
            }`}>
              <div className="flex items-center">
                <div className={`flex-shrink-0 ${
                  premiumStatus.is_premium ? 'text-green-400' : 'text-yellow-400'
                }`}>
                  {premiumStatus.is_premium ? (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div className="ml-3">
                  <p className={`text-sm font-medium ${
                    premiumStatus.is_premium ? 'text-green-800' : 'text-yellow-800'
                  }`}>
                    {premiumStatus.is_premium ? 'Premium Active' : 'Free Plan'}
                  </p>
                  <p className={`text-sm ${
                    premiumStatus.is_premium ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {premiumStatus.is_premium 
                      ? 'You have access to all premium features'
                      : 'Upgrade to unlock unlimited prompts and advanced features'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-8 max-w-md mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-2">
          {/* Free Plan */}
          <div className="border border-gray-200 rounded-lg shadow-sm divide-y divide-gray-200">
            <div className="p-6">
              <h2 className="text-lg leading-6 font-medium text-gray-900">Free</h2>
              <p className="mt-4 text-sm text-gray-500">Perfect for getting started with VibeCoding</p>
              <p className="mt-8">
                <span className="text-4xl font-extrabold text-gray-900">$0</span>
                <span className="text-base font-medium text-gray-500">/month</span>
              </p>
              <button
                disabled={true}
                className="mt-8 block w-full bg-gray-300 border border-gray-300 rounded-md py-2 text-sm font-semibold text-gray-500 cursor-not-allowed"
              >
                Current Plan
              </button>
            </div>
            <div className="pt-6 pb-8 px-6">
              <h3 className="text-xs font-medium text-gray-900 tracking-wide uppercase">What's included</h3>
              <ul className="mt-6 space-y-4">
                <li className="flex space-x-3">
                  <svg className="flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-gray-500">5 AI-generated prompts per month</span>
                </li>
                <li className="flex space-x-3">
                  <svg className="flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-gray-500">Basic project management</span>
                </li>
                <li className="flex space-x-3">
                  <svg className="flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-gray-500">Community support</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Premium Plan */}
          {products.map((product) => (
            <div key={product.id} className="border border-blue-200 rounded-lg shadow-sm divide-y divide-gray-200 relative">
              {/* Popular badge */}
              <div className="absolute top-0 right-6 transform -translate-y-1/2">
                <span className="inline-flex px-4 py-1 rounded-full text-xs font-semibold tracking-wide bg-blue-600 text-white">
                  Most Popular
                </span>
              </div>
              
              <div className="p-6">
                <h2 className="text-lg leading-6 font-medium text-gray-900">{product.name}</h2>
                <p className="mt-4 text-sm text-gray-500">{product.description}</p>
                <p className="mt-8">
                  <span className="text-4xl font-extrabold text-gray-900">{product.price}</span>
                  <span className="text-base font-medium text-gray-500">/{product.interval}</span>
                </p>
                <button
                  onClick={() => handleUpgrade(product.id)}
                  disabled={purchasing || (premiumStatus?.is_premium && true)}
                  className={`mt-8 block w-full border rounded-md py-2 text-sm font-semibold text-center ${
                    premiumStatus?.is_premium
                      ? 'bg-green-600 border-green-600 text-white cursor-default'
                      : purchasing
                      ? 'bg-gray-300 border-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 border-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {premiumStatus?.is_premium
                    ? 'Current Plan'
                    : purchasing
                    ? 'Processing...'
                    : 'Upgrade Now'
                  }
                </button>
              </div>
              
              <div className="pt-6 pb-8 px-6">
                <h3 className="text-xs font-medium text-gray-900 tracking-wide uppercase">What's included</h3>
                <ul className="mt-6 space-y-4">
                  {product.features.map((feature, index) => (
                    <li key={index} className="flex space-x-3">
                      <svg className="flex-shrink-0 h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm text-gray-500">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-16">
          <h3 className="text-lg font-medium text-gray-900 text-center mb-8">Frequently Asked Questions</h3>
          <div className="max-w-3xl mx-auto">
            <div className="space-y-6">
              <div>
                <h4 className="font-medium text-gray-900">Can I cancel my subscription at any time?</h4>
                <p className="mt-2 text-sm text-gray-600">
                  Yes, you can cancel your subscription at any time. Your premium features will remain active until the end of your current billing period.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">What payment methods do you accept?</h4>
                <p className="mt-2 text-sm text-gray-600">
                  We accept all major credit cards (Visa, MasterCard, American Express) and other payment methods through our secure payment processor.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Is there a free trial?</h4>
                <p className="mt-2 text-sm text-gray-600">
                  Our free plan gives you a taste of VibeCoding with 5 AI-generated prompts per month. You can upgrade to premium at any time to unlock unlimited access.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}