import React, { useState, useEffect } from 'react';
import { DollarSign, FileText, CreditCard, Calendar, CheckCircle, AlertCircle } from 'lucide-react';

const BillingPage = () => {
  const [statements, setStatements] = useState([]);
  const [selectedStatement, setSelectedStatement] = useState(null);
  const [statementDetails, setStatementDetails] = useState(null);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [accountNumber, setAccountNumber] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('statements');

  useEffect(() => {
    fetchStatements();
    fetchPaymentHistory();
  }, []);

  const fetchStatements = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://localhost:8000/api/billing/statements', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStatements(data.statements);
        setAccountNumber(data.account_number);
      } else {
        const errorData = await response.json();
        setError(errorData.error);
      }
    } catch (err) {
      setError('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  };

  const fetchPaymentHistory = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://localhost:8000/api/billing/payment-history', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setPaymentHistory(data.payments);
      }
    } catch (err) {
      console.error('Failed to load payment history:', err);
    }
  };

  const fetchStatementDetails = async (statementId) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`http://localhost:8000/api/billing/statements/${statementId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setStatementDetails(data);
        setSelectedStatement(statementId);
      }
    } catch (err) {
      console.error('Failed to load statement details:', err);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatMonth = (monthString) => {
    const [year, month] = monthString.split('-');
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading billing information...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-yellow-600 mt-0.5" />
            <div>
              <p className="text-yellow-800 font-semibold">Billing Not Available</p>
              <p className="text-yellow-700 text-sm mt-1">{error}</p>
              <p className="text-yellow-700 text-sm mt-2">
                Billing statements are only available for contract customers.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-2">
                <FileText className="w-8 h-8" />
                Billing & Invoices
              </h1>
              {accountNumber && (
                <p className="text-gray-600">Account Number: <span className="font-mono font-semibold">{accountNumber}</span></p>
              )}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('statements')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'statements'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Statements
              </button>
              <button
                onClick={() => setActiveTab('payments')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'payments'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Payment History
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'statements' && (
              <div className="space-y-4">
                {statements.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No billing statements available</p>
                ) : (
                  statements.map((statement) => (
                    <div
                      key={statement.statement_id}
                      className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => fetchStatementDetails(statement.statement_id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-blue-50 rounded-lg">
                            <Calendar className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-gray-800">
                              {formatMonth(statement.statement_month)}
                            </p>
                            <p className="text-sm text-gray-600">
                              Statement ID: {statement.statement_id}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-gray-800">
                            {formatCurrency(statement.total_amount)}
                          </p>
                          <span
                            className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                              statement.status === 'paid'
                                ? 'bg-green-50 text-green-700'
                                : 'bg-yellow-50 text-yellow-700'
                            }`}
                          >
                            {statement.status === 'paid' ? (
                              <span className="flex items-center gap-1">
                                <CheckCircle className="w-4 h-4" />
                                Paid
                              </span>
                            ) : (
                              'Unpaid'
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'payments' && (
              <div className="space-y-4">
                {paymentHistory.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No payment history available</p>
                ) : (
                  paymentHistory.map((payment) => (
                    <div
                      key={payment.payment_id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="p-3 bg-green-50 rounded-lg">
                            <CreditCard className="w-6 h-6 text-green-600" />
                          </div>
                          <div>
                            <p className="font-semibold text-gray-800">
                              {formatDate(payment.date_paid)}
                            </p>
                            <p className="text-sm text-gray-600 capitalize">
                              {payment.method.replace('_', ' ')}
                              {payment.tracking_number && ` • Tracking #${payment.tracking_number}`}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xl font-bold text-green-600">
                            {formatCurrency(payment.amount)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* Statement Details Modal */}
        {statementDetails && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-800">
                Statement Details - {formatMonth(statementDetails.statement.statement_month)}
              </h2>
              <button
                onClick={() => setStatementDetails(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Amount</p>
                  <p className="text-3xl font-bold text-gray-800">
                    {formatCurrency(statementDetails.statement.total_amount)}
                  </p>
                </div>
                <span
                  className={`px-4 py-2 rounded-lg font-semibold ${
                    statementDetails.statement.status === 'paid'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}
                >
                  {statementDetails.statement.status === 'paid' ? 'Paid' : 'Unpaid'}
                </span>
              </div>
            </div>

            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Packages ({statementDetails.packages.length})
            </h3>

            <div className="space-y-3">
              {statementDetails.packages.map((pkg) => (
                <div
                  key={pkg.tracking_number}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800">
                        Tracking #{pkg.tracking_number}
                      </p>
                      <p className="text-sm text-gray-600">
                        To: {pkg.recipient_name} ({pkg.recipient_location})
                      </p>
                      <p className="text-sm text-gray-500">
                        {pkg.service} • {pkg.weight} lbs • {formatDate(pkg.date_shipped)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-800">
                        {formatCurrency(pkg.cost)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {statementDetails.statement.status === 'unpaid' && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Payment Due:</strong> This statement is currently unpaid. 
                  Please contact our billing department to make a payment.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingPage;
