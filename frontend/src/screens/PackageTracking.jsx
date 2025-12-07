import React, { useState, useEffect } from 'react';
import { Package, MapPin, Clock, CheckCircle, Truck, Plane, Warehouse } from 'lucide-react';

const PackageTracking = () => {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [packageData, setPackageData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userPackages, setUserPackages] = useState([]);

  // Fetch user's packages on component mount
  useEffect(() => {
    fetchUserPackages();
  }, []);

  const fetchUserPackages = async () => {
    try {
      // Get token from localStorage (you'd implement proper auth)
      const token = localStorage.getItem('authToken');
      
      const response = await fetch('http://localhost:8000/api/user/packages', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserPackages(data.packages);
      }
    } catch (err) {
      console.error('Error fetching packages:', err);
    }
  };

  const handleTrackPackage = async (e) => {
    e.preventDefault();
    
    if (!trackingNumber.trim()) {
      setError('Please enter a tracking number');
      return;
    }

    setLoading(true);
    setError('');
    setPackageData(null);

    try {
      // Get token from localStorage
      const token = localStorage.getItem('authToken');
      
      const response = await fetch(`http://localhost:8000/api/tracking/${trackingNumber}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Package not found');
      }

      const data = await response.json();
      setPackageData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getLocationIcon = (type) => {
    switch (type) {
      case 'truck':
        return <Truck className="w-5 h-5" />;
      case 'plane':
        return <Plane className="w-5 h-5" />;
      case 'warehouse':
        return <Warehouse className="w-5 h-5" />;
      default:
        return <MapPin className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes('delivered')) return 'text-green-600 bg-green-50';
    if (statusLower.includes('transit') || statusLower.includes('departed')) return 'text-blue-600 bg-blue-50';
    if (statusLower.includes('arrived')) return 'text-purple-600 bg-purple-50';
    return 'text-gray-600 bg-gray-50';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <Package className="w-8 h-8" />
            Track Your Package
          </h1>

          {/* Tracking Input */}
          <div className="flex gap-3 mb-6">
            <input
              type="text"
              value={trackingNumber}
              onChange={(e) => setTrackingNumber(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleTrackPackage(e)}
              placeholder="Enter tracking number"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              onClick={handleTrackPackage}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? 'Tracking...' : 'Track'}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {/* Package Details */}
        {packageData && (
          <div className="space-y-6">
            {/* Current Status Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Current Status</h2>
              
              {packageData.current_status ? (
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-full ${getStatusColor(packageData.current_status.status)}`}>
                    {packageData.package.date_delivered ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      <Truck className="w-6 h-6" />
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="text-2xl font-bold text-gray-800 mb-1">
                      {packageData.current_status.status}
                    </p>
                    <p className="text-gray-600 mb-1">
                      {packageData.current_status.location}
                      {packageData.current_status.city && `, ${packageData.current_status.city}`}
                      {packageData.current_status.state && `, ${packageData.current_status.state}`}
                    </p>
                    <p className="text-sm text-gray-500 flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDate(packageData.current_status.timestamp)}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No tracking information available</p>
              )}
            </div>

            {/* Package Details Card */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Package Details</h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* Sender Info */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">From</h3>
                  <p className="text-gray-800">{packageData.package.sender.name}</p>
                  <p className="text-gray-600 text-sm">{packageData.package.sender.address}</p>
                  <p className="text-gray-600 text-sm">
                    {packageData.package.sender.city}, {packageData.package.sender.state} {packageData.package.sender.zip}
                  </p>
                </div>

                {/* Recipient Info */}
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">To</h3>
                  <p className="text-gray-800">{packageData.package.recipient.name}</p>
                  <p className="text-gray-600 text-sm">{packageData.package.recipient.address}</p>
                  <p className="text-gray-600 text-sm">
                    {packageData.package.recipient.city}, {packageData.package.recipient.state} {packageData.package.recipient.zip}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Service</p>
                  <p className="font-semibold text-gray-800">{packageData.package.service}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Weight</p>
                  <p className="font-semibold text-gray-800">{packageData.package.weight} lb</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Shipped</p>
                  <p className="font-semibold text-gray-800">{formatDate(packageData.package.date_shipped)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Delivered</p>
                  <p className="font-semibold text-gray-800">
                    {packageData.package.date_delivered ? formatDate(packageData.package.date_delivered) : 'In Transit'}
                  </p>
                </div>
              </div>

              {packageData.package.delivered_signature && (
                <div className="mt-4 p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-green-800">
                    <strong>Signed by:</strong> {packageData.package.delivered_signature}
                  </p>
                </div>
              )}
            </div>

            {/* Tracking History */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Tracking History</h2>
              
              <div className="space-y-4">
                {packageData.tracking_history.map((event, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`p-2 rounded-full ${getStatusColor(event.status)}`}>
                        {getLocationIcon(event.location_type)}
                      </div>
                      {index < packageData.tracking_history.length - 1 && (
                        <div className="w-0.5 h-full bg-gray-300 my-1" />
                      )}
                    </div>
                    
                    <div className="flex-1 pb-6">
                      <p className="font-semibold text-gray-800">{event.status}</p>
                      <p className="text-sm text-gray-600">
                        {event.location}
                        {event.city && `, ${event.city}`}
                        {event.state && `, ${event.state}`}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">{formatDate(event.timestamp)}</p>
                      {event.notes && (
                        <p className="text-sm text-gray-600 mt-1 italic">{event.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* User's Recent Packages */}
        {!packageData && userPackages.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Your Recent Packages</h2>
            
            <div className="space-y-3">
              {userPackages.map((pkg) => (
                <div
                  key={pkg.tracking_number}
                  onClick={() => setTrackingNumber(pkg.tracking_number.toString())}
                  className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-gray-800">
                        Tracking #: {pkg.tracking_number}
                      </p>
                      <p className="text-sm text-gray-600">
                        To: {pkg.recipient_name} - {pkg.recipient_location}
                      </p>
                      <p className="text-sm text-gray-500">
                        Shipped: {formatDate(pkg.date_shipped)}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pkg.current_status)}`}>
                      {pkg.current_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PackageTracking;
