import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import {
  Users, Eye, Heart, ShoppingCart, CheckCircle,
  TrendingDown, Clock, AlertTriangle, RefreshCw
} from 'lucide-react';


const CustomerJourneyTracker = () => {
  const [funnelData, setFunnelData] = useState(null);
  const [attributionData, setAttributionData] = useState(null);
  const [timeToConversion, setTimeToConversion] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJourneyData();
  }, []);

  const fetchJourneyData = async () => {
    try {
      setLoading(true);
      
      // Fetch funnel data
      const funnelRes = await fetch(`${BACKEND_URL}/api/marketing-analytics/customer-journey-funnel`);
      const funnelJson = await funnelRes.json();
      setFunnelData(funnelJson);
      
      // Fetch attribution data
      const attrRes = await fetch(`${BACKEND_URL}/api/marketing-analytics/lead-source-attribution`);
      const attrJson = await attrRes.json();
      setAttributionData(attrJson);
      
      // Fetch time to conversion
      const timeRes = await fetch(`${BACKEND_URL}/api/marketing-analytics/time-to-conversion`);
      const timeJson = await timeRes.json();
      setTimeToConversion(timeJson);
      
    } catch (error) {
      console.error('Error fetching journey data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStageIcon = (stage) => {
    const icons = {
      'awareness': <Eye className="w-8 h-8" />,
      'interest': <Users className="w-8 h-8" />,
      'consideration': <Heart className="w-8 h-8" />,
      'intent': <ShoppingCart className="w-8 h-8" />,
      'purchase': <CheckCircle className="w-8 h-8" />
    };
    return icons[stage] || <Users className="w-8 h-8" />;
  };

  const getStageColor = (stage) => {
    const colors = {
      'awareness': 'bg-blue-500',
      'interest': 'bg-green-500',
      'consideration': 'bg-yellow-500',
      'intent': 'bg-orange-500',
      'purchase': 'bg-purple-500'
    };
    return colors[stage] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading customer journey data...</p>
        </div>
      </div>
    );
  }

  const summary = funnelData?.summary || {};

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Customer Journey Funnel</h1>
            <p className="text-gray-600 mt-1">Track customer progression from awareness to purchase</p>
          </div>
          <button
            onClick={fetchJourneyData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Total Leads</h3>
              <Users className="w-6 h-6 text-blue-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{summary.total_leads || 0}</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Conversions</h3>
              <CheckCircle className="w-6 h-6 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{summary.total_purchases || 0}</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Conv. Rate</h3>
              <TrendingDown className="w-6 h-6 text-orange-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{summary.overall_conversion_rate || 0}%</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Avg Time</h3>
              <Clock className="w-6 h-6 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {timeToConversion?.metrics?.average_days || 0}
              <span className="text-base font-normal text-gray-600"> days</span>
            </p>
          </div>
        </div>

        {/* Bottleneck Alert */}
        {summary.bottleneck_stage && (
          <div className="bg-red-50 border-l-4 border-red-500 p-6 mb-8 rounded-lg">
            <div className="flex items-start">
              <AlertTriangle className="w-6 h-6 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-red-900 font-semibold text-lg">Bottleneck Identified</h3>
                <p className="text-red-700 mt-1">
                  <strong>{summary.bottleneck_stage}</strong> stage has the highest drop-off rate at{' '}
                  <strong>{summary.bottleneck_drop_off?.toFixed(1)}%</strong>
                </p>
                <p className="text-red-600 text-sm mt-2">
                  💡 <strong>Recommendation:</strong> Focus on improving engagement at the {summary.bottleneck_stage} stage
                  to reduce customer drop-off and increase conversions.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Funnel Visualization */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Conversion Funnel</h2>
          
          <div className="space-y-6">
            {funnelData?.funnel?.map((stage, index) => {
              const isLast = index === funnelData.funnel.length - 1;
              const barWidth = stage.percentage;
              
              return (
                <div key={stage.stage}>
                  {/* Stage Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className={`${getStageColor(stage.stage)} text-white p-2 rounded-lg`}>
                        {getStageIcon(stage.stage)}
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{stage.label}</h3>
                        <p className="text-sm text-gray-600">{stage.description}</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">{stage.count}</p>
                      <p className="text-sm text-gray-600">{stage.percentage}%</p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getStageColor(stage.stage)} transition-all duration-500`}
                      style={{ width: `${barWidth}%` }}
                    >
                      <div className="flex items-center justify-between h-full px-4 text-white text-sm font-medium">
                        <span>{stage.count} customers</span>
                        <span>{stage.percentage}%</span>
                      </div>
                    </div>
                  </div>

                  {/* Drop-off Indicator */}
                  {!isLast && stage.drop_off > 0 && (
                    <div className="flex items-center gap-2 mt-2 text-red-600 text-sm">
                      <TrendingDown className="w-4 h-4" />
                      <span>
                        {stage.drop_off} customers dropped ({stage.drop_off_rate?.toFixed(1)}%)
                      </span>
                    </div>
                  )}

                  {/* Arrow */}
                  {!isLast && (
                    <div className="flex justify-center my-4">
                      <div className="text-gray-400 text-3xl">↓</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Lead Source Attribution */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Lead Source Quality</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Leads</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conversions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conv. Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rev/Lead</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quality</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {attributionData?.attribution?.map((source, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {source.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {source.leads}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {source.conversions}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {source.conversion_rate}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{source.revenue?.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{source.revenue_per_lead?.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        source.quality_rating === 'High' ? 'bg-green-100 text-green-800' :
                        source.quality_rating === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {source.quality_rating}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Time to Conversion Metrics */}
        {timeToConversion?.metrics && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Conversion Timeline</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-gray-600 text-sm mb-2">Average Time</p>
                <p className="text-4xl font-bold text-blue-600">
                  {timeToConversion.metrics.average_days}
                  <span className="text-lg text-gray-600"> days</span>
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-gray-600 text-sm mb-2">Median Time</p>
                <p className="text-4xl font-bold text-green-600">
                  {timeToConversion.metrics.median_days}
                  <span className="text-lg text-gray-600"> days</span>
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-gray-600 text-sm mb-2">Fastest</p>
                <p className="text-4xl font-bold text-orange-600">
                  {timeToConversion.metrics.fastest_days}
                  <span className="text-lg text-gray-600"> days</span>
                </p>
              </div>
              
              <div className="text-center">
                <p className="text-gray-600 text-sm mb-2">Slowest</p>
                <p className="text-4xl font-bold text-purple-600">
                  {timeToConversion.metrics.slowest_days}
                  <span className="text-lg text-gray-600"> days</span>
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerJourneyTracker;
