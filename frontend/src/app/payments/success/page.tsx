'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../contexts/AuthContext';
import api from '../../../../services/api';

export default function PaymentSuccessPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [checkoutDetails, setCheckoutDetails] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      const checkoutId = searchParams.get('checkout_id');
      if (checkoutId) {
        loadCheckoutDetails(checkoutId);
      } else {
        setLoading(false);
      }
    }
  }, [user, isLoading, router, searchParams]);

  const loadCheckoutDetails = async (checkoutId: string) => {
    try {
      setLoading(true);
      const details = await api.payments.getCheckoutDetails(checkoutId);
      setCheckoutDetails(details);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load checkout details');
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    router.push('/dashboard');
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error ? (
            // Error State
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <div className="mt-3">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Payment Error
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    {error}
                  </p>
                </div>
              </div>
              <div className="mt-6">
                <button
                  onClick={() => router.push('/pricing')}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Back to Pricing
                </button>
              </div>
            </div>
          ) : (
            // Success State
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div className="mt-3">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Payment Successful!
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    Welcome to VibeCoding Premium! Your account has been upgraded and you now have access to all premium features.
                  </p>
                </div>
              </div>

              {/* Premium Features */}
              <div className="mt-6">
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <h4 className="text-sm font-medium text-blue-900 mb-3">
                    You now have access to:
                  </h4>
                  <ul className="text-sm text-blue-800 space-y-2">
                    <li className="flex items-center">
                      <svg className="h-4 w-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Unlimited AI-generated prompts
                    </li>
                    <li className="flex items-center">
                      <svg className="h-4 w-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Advanced export formats
                    </li>
                    <li className="flex items-center">
                      <svg className="h-4 w-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Priority customer support
                    </li>
                    <li className="flex items-center">
                      <svg className="h-4 w-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Early access to new features
                    </li>
                  </ul>
                </div>
              </div>

              {/* Checkout Details */}
              {checkoutDetails && (
                <div className="mt-6 text-left bg-gray-50 rounded-md p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Payment Details</h4>
                  <div className="text-xs text-gray-600 space-y-1">
                    <p><span className="font-medium">Transaction ID:</span> {checkoutDetails.checkout_id}</p>
                    <p><span className="font-medium">Status:</span> {checkoutDetails.status}</p>
                    {checkoutDetails.amount && (
                      <p><span className="font-medium">Amount:</span> {checkoutDetails.currency} {(checkoutDetails.amount / 100).toFixed(2)}</p>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-6 space-y-3">
                <button
                  onClick={handleContinue}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Continue to Dashboard
                </button>
                <button
                  onClick={() => router.push('/pricing')}
                  className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  View Subscription Details
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-500">
          Need help? Contact our{' '}
          <a href="mailto:support@vibecoding.com" className="text-blue-600 hover:text-blue-500">
            support team
          </a>
        </p>
      </div>
    </div>
  );
}