// src/screens/Home.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, Truck, Clock, Shield, MapPin, TrendingUp, ArrowRight, CheckCircle } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const [trackingNumber, setTrackingNumber] = useState('');
  const isLoggedIn = localStorage.getItem('authToken');

  const handleQuickTrack = (e) => {
    e.preventDefault();
    if (trackingNumber.trim()) {
      navigate('/track');
    }
  };

  const features = [
    {
      icon: <Truck className="w-8 h-8" />,
      title: 'Fast Delivery',
      description: 'Overnight, 2-day, and ground shipping options to meet your needs'
    },
    {
      icon: <MapPin className="w-8 h-8" />,
      title: 'Real-Time Tracking',
      description: 'Track your packages from pickup to delivery with detailed updates'
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Secure Shipping',
      description: 'Your packages are handled with care and protected every step of the way'
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: '24/7 Support',
      description: 'Our team is always available to help with your shipping needs'
    }
  ];

  const services = [
    {
      name: 'Overnight Express',
      description: 'Next-day delivery for urgent shipments',
      price: 'From $25.99',
      features: ['Guaranteed delivery', 'Real-time tracking', 'Signature required']
    },
    {
      name: '2-Day Shipping',
      description: 'Fast and affordable delivery option',
      price: 'From $19.99',
      features: ['Two-day delivery', 'Package protection', 'Email updates']
    },
    {
      name: 'Ground Shipping',
      description: 'Cost-effective solution for non-urgent packages',
      price: 'From $9.99',
      features: ['3-5 day delivery', 'Standard tracking', 'Reliable service']
    }
  ];

  const stats = [
    { number: '10M+', label: 'Packages Delivered' },
    { number: '50K+', label: 'Happy Customers' },
    { number: '100+', label: 'Cities Served' },
    { number: '99.9%', label: 'On-Time Delivery' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-purple-700 to-purple-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 py-24 sm:py-32">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-white bg-opacity-20 rounded-full">
                <Package className="w-16 h-16" />
              </div>
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold mb-6">
              Fast, Reliable Package Delivery
            </h1>
            <p className="text-xl sm:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              Ship packages with confidence. Track every step. Delivered on time, every time.
            </p>

            {/* Quick Track Input */}
            <div className="max-w-2xl mx-auto mb-8">
              <div className="bg-white rounded-lg shadow-xl p-6">
                <h3 className="text-gray-800 text-lg font-semibold mb-4">Track Your Package</h3>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={trackingNumber}
                    onChange={(e) => setTrackingNumber(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleQuickTrack(e)}
                    placeholder="Enter tracking number"
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-800"
                  />
                  <button
                    onClick={handleQuickTrack}
                    className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium transition-colors flex items-center gap-2"
                  >
                    Track <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap justify-center gap-4">
              <button
                onClick={() => navigate(isLoggedIn ? '/ship' : '/register')}
                className="px-8 py-4 bg-white text-purple-700 rounded-lg hover:bg-gray-100 font-semibold text-lg transition-colors shadow-lg"
              >
                {isLoggedIn ? 'Ship a Package' : 'Get Started'}
              </button>
              <button
                onClick={() => navigate('/track')}
                className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-lg hover:bg-white hover:text-purple-700 font-semibold text-lg transition-colors"
              >
                View My Packages
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-12 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-purple-700 mb-2">{stat.number}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">Why Choose Us?</h2>
            <p className="text-xl text-gray-600">Experience the difference with our premium shipping services</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow">
                <div className="p-3 bg-purple-50 rounded-lg inline-block mb-4 text-purple-700">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Services Section */}
      <div className="bg-gray-50 py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">Our Shipping Services</h2>
            <p className="text-xl text-gray-600">Choose the service that fits your needs and budget</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-8 hover:shadow-xl transition-shadow">
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">{service.name}</h3>
                  <p className="text-gray-600 mb-4">{service.description}</p>
                  <div className="text-3xl font-bold text-purple-700">{service.price}</div>
                </div>
                <div className="space-y-3">
                  {service.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => navigate(isLoggedIn ? '/ship' : '/register')}
                  className="w-full mt-6 px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 font-medium transition-colors"
                >
                  Select Service
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">How It Works</h2>
            <p className="text-xl text-gray-600">Shipping made simple in three easy steps</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-700 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Create Shipment</h3>
              <p className="text-gray-600">
                Enter sender and recipient details, choose your service, and get instant pricing
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Drop Off Package</h3>
              <p className="text-gray-600">
                Drop your package at any of our locations or schedule a pickup from your door
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">Track & Deliver</h3>
              <p className="text-gray-600">
                Monitor your package in real-time and receive delivery confirmation with signature
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-purple-700 to-purple-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Ship?</h2>
          <p className="text-xl mb-8 text-purple-100">
            Join thousands of satisfied customers who trust us with their deliveries
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={() => navigate('/register')}
              className="px-8 py-4 bg-white text-purple-700 rounded-lg hover:bg-gray-100 font-semibold text-lg transition-colors shadow-lg"
            >
              Create Free Account
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-lg hover:bg-white hover:text-purple-700 font-semibold text-lg transition-colors"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-gray-300 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Package className="w-8 h-8 text-purple-400" />
                <span className="text-xl font-bold text-white">QuickShip</span>
              </div>
              <p className="text-sm">Fast, reliable package delivery services you can trust.</p>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Services</h4>
              <ul className="space-y-2 text-sm">
                <li className="hover:text-white cursor-pointer">Overnight Delivery</li>
                <li className="hover:text-white cursor-pointer">2-Day Shipping</li>
                <li className="hover:text-white cursor-pointer">Ground Shipping</li>
                <li className="hover:text-white cursor-pointer">International</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li className="hover:text-white cursor-pointer">About Us</li>
                <li className="hover:text-white cursor-pointer">Careers</li>
                <li className="hover:text-white cursor-pointer">Contact</li>
                <li className="hover:text-white cursor-pointer">Locations</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-white mb-4">Support</h4>
              <ul className="space-y-2 text-sm">
                <li className="hover:text-white cursor-pointer">Help Center</li>
                <li className="hover:text-white cursor-pointer">Track Package</li>
                <li className="hover:text-white cursor-pointer">Shipping Rates</li>
                <li className="hover:text-white cursor-pointer">Terms of Service</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2025 QuickShip. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
