import React, { useState, useEffect } from 'react';
import { Package, DollarSign, AlertCircle, CheckCircle } from 'lucide-react';

const ShipPackage = () => {
  const [services, setServices] = useState([]);
  const [customerProfile, setCustomerProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [trackingNumber, setTrackingNumber] = useState(null);

  const [formData, setFormData] = useState({
    sender_name: '',
    sender_addr1: '',
    sender_addr2: '',
    sender_city: '',
    sender_state: '',
    sender_zip: '',
    recipient_name: '',
    recipient_addr1: '',
    recipient_addr2: '',
    recipient_city: '',
    recipient_state: '',
    recipient_zip: '',
    service_id: '',
    weight_lb: '',
    is_hazardous: false,
    is_international: false,
    declared_value: '',
    customs_desc: '',
    payment_type: 'credit_card'
  });

  useEffect(() => {
    fetchServices();
    fetchCustomerProfile();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/services');
      const data = await response.json();
      setServices(data.services);
    } catch (err) {
      console.error('Error fetching services:', err);
    }
  };

  const fetchCustomerProfile = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://localhost:5000/api/customer/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.exists) {
        setCustomerProfile(data.customer);
        // Pre-fill sender info from profile
        setFormData(prev => ({
          ...prev,
          sender_name: data.customer.name,
          sender_addr1: data.customer.address_line1,
          sender_addr2: data.customer.address_line2 || '',
          sender_city: data.customer.city,
          sender_state: data.customer.state,
          sender_zip: data.customer.zip
        }));
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const token = localStorage.getItem('authToken');
      
      const response = await fetch('http://localhost:5000/api/ship', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          weight_lb: parseFloat(formData.weight_lb),
          declared_value: formData.declared_value ? parseFloat(formData.declared_value) : null,
          service_id: parseInt(formData.service_id)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create shipment');
      }

      const data = await response.json();
      setSuccess(true);
      setTrackingNumber(data.tracking_number);
      
      // Reset form
      setFormData({
        ...formData,
        recipient_name: '',
        recipient_addr1: '',
        recipient_addr2: '',
        recipient_city: '',
        recipient_state: '',
        recipient_zip: '',
        weight_lb: '',
        is_hazardous: false,
        is_international: false,
        declared_value: '',
        customs_desc: ''
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedService = services.find(s => s.service_id === parseInt(formData.service_id));

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Package className="w-8 h-8" />
            Ship a Package
          </h1>
          <p className="text-gray-600">Fill out the details below to create a new shipment</p>
        </div>

        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <p className="text-green-800 font-semibold">Shipment Created Successfully!</p>
              <p className="text-green-700 text-sm">
                Your tracking number is: <span className="font-mono font-bold">{trackingNumber}</span>
              </p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="space-y-6">
            {/* Sender Information */}
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">Sender Information</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    name="sender_name"
                    value={formData.sender_name}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 1 *
                  </label>
                  <input
                    type="text"
                    name="sender_addr1"
                    value={formData.sender_addr1}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 2
                  </label>
                  <input
                    type="text"
                    name="sender_addr2"
                    value={formData.sender_addr2}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    City *
                  </label>
                  <input
                    type="text"
                    name="sender_city"
                    value={formData.sender_city}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    State *
                  </label>
                  <input
                    type="text"
                    name="sender_state"
                    value={formData.sender_state}
                    onChange={handleChange}
                    required
                    maxLength="2"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ZIP Code *
                  </label>
                  <input
                    type="text"
                    name="sender_zip"
                    value={formData.sender_zip}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Recipient Information</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name *
                  </label>
                  <input
                    type="text"
                    name="recipient_name"
                    value={formData.recipient_name}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 1 *
                  </label>
                  <input
                    type="text"
                    name="recipient_addr1"
                    value={formData.recipient_addr1}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Address Line 2
                  </label>
                  <input
                    type="text"
                    name="recipient_addr2"
                    value={formData.recipient_addr2}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    City *
                  </label>
                  <input
                    type="text"
                    name="recipient_city"
                    value={formData.recipient_city}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    State *
                  </label>
                  <input
                    type="text"
                    name="recipient_state"
                    value={formData.recipient_state}
                    onChange={handleChange}
                    required
                    maxLength="2"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    ZIP Code *
                  </label>
                  <input
                    type="text"
                    name="recipient_zip"
                    value={formData.recipient_zip}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Package Details</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Service Type *
                  </label>
                  <select
                    name="service_id"
                    value={formData.service_id}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a service...</option>
                    {services.map(service => (
                      <option key={service.service_id} value={service.service_id}>
                        {service.name} - ${service.base_price} ({service.delivery_speed})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Weight (lbs) *
                  </label>
                  <input
                    type="number"
                    name="weight_lb"
                    value={formData.weight_lb}
                    onChange={handleChange}
                    required
                    step="0.1"
                    min="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {selectedService && formData.weight_lb && (
                    <p className="text-sm text-gray-600 mt-1">
                      Max weight: {selectedService.max_weight_lb} lbs
                    </p>
                  )}
                </div>

                <div className="md:col-span-2 flex gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      name="is_hazardous"
                      checked={formData.is_hazardous}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm font-medium text-gray-700">Hazardous Materials</span>
                  </label>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      name="is_international"
                      checked={formData.is_international}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm font-medium text-gray-700">International Shipment</span>
                  </label>
                </div>

                {formData.is_international && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Declared Value (USD)
                      </label>
                      <input
                        type="number"
                        name="declared_value"
                        value={formData.declared_value}
                        onChange={handleChange}
                        step="0.01"
                        min="0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Customs Description
                      </label>
                      <input
                        type="text"
                        name="customs_desc"
                        value={formData.customs_desc}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Payment</h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Method *
                </label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="payment_type"
                      value="credit_card"
                      checked={formData.payment_type === 'credit_card'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Credit Card</span>
                  </label>
                  {customerProfile?.has_contract && (
                    <label className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="payment_type"
                        value="account"
                        checked={formData.payment_type === 'account'}
                        onChange={handleChange}
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-sm text-gray-700">
                        Bill to Account #{customerProfile.account_number}
                      </span>
                    </label>
                  )}
                  <label className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="payment_type"
                      value="prepaid"
                      checked={formData.payment_type === 'prepaid'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm text-gray-700">Prepaid (Recipient Pays)</span>
                  </label>
                </div>
              </div>

              {selectedService && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg flex items-center justify-between">
                  <span className="font-medium text-gray-700">Estimated Cost:</span>
                  <span className="text-2xl font-bold text-blue-600 flex items-center gap-1">
                    <DollarSign className="w-6 h-6" />
                    {selectedService.base_price.toFixed(2)}
                  </span>
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-4">
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {loading ? 'Creating Shipment...' : 'Create Shipment'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShipPackage;
