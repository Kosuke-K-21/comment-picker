import React from 'react';
import { AlertCondition } from './AlertSettings';

interface AlertResult {
  condition: AlertCondition;
  triggered: boolean;
  currentValue: number;
  message: string;
}

interface AlertCheckerProps {
  conditions: AlertCondition[];
  statistics?: any;
}

export const checkAlerts = (conditions: AlertCondition[], statistics: any): AlertResult[] => {
  if (!statistics || !conditions.length) return [];

  return conditions
    .filter(condition => condition.enabled)
    .map(condition => {
      let currentValue = 0;
      let triggered = false;

      // Calculate current value based on condition
      if (condition.target === 'sentiment') {
        if (condition.type === 'percentage') {
          switch (condition.targetValue) {
            case 'ポジティブ':
              currentValue = statistics.overall_sentiment?.positive_percentage || 0;
              break;
            case '中立':
              currentValue = statistics.overall_sentiment?.neutral_percentage || 0;
              break;
            case 'ネガティブ':
              currentValue = statistics.overall_sentiment?.negative_percentage || 0;
              break;
          }
        } else {
          switch (condition.targetValue) {
            case 'ポジティブ':
              currentValue = statistics.overall_sentiment?.positive || 0;
              break;
            case '中立':
              currentValue = statistics.overall_sentiment?.neutral || 0;
              break;
            case 'ネガティブ':
              currentValue = statistics.overall_sentiment?.negative || 0;
              break;
          }
        }
      } else if (condition.target === 'category') {
        const categoryStats = statistics.category_statistics?.find(
          (cat: any) => cat.category === condition.targetValue
        );
        if (categoryStats) {
          currentValue = condition.type === 'percentage' 
            ? categoryStats.percentage 
            : categoryStats.count;
        }
      }

      // Check if condition is triggered
      switch (condition.operator) {
        case 'gte':
          triggered = currentValue >= condition.threshold;
          break;
        case 'lte':
          triggered = currentValue <= condition.threshold;
          break;
        case 'eq':
          triggered = currentValue === condition.threshold;
          break;
      }

      const message = `${condition.targetValue} が ${currentValue}${condition.type === 'percentage' ? '%' : '件'} (閾値: ${condition.threshold}${condition.type === 'percentage' ? '%' : '件'})`;

      return {
        condition,
        triggered,
        currentValue,
        message
      };
    });
};

const AlertChecker: React.FC<AlertCheckerProps> = ({ conditions, statistics }) => {
  const alertResults = checkAlerts(conditions, statistics);
  const triggeredAlerts = alertResults.filter(result => result.triggered);

  if (triggeredAlerts.length === 0) {
    return null;
  }

  return (
    <div className="alert-notifications">
      <div className="alert-header">
        <span className="alert-icon">🚨</span>
        <h4>アラート通知 ({triggeredAlerts.length}件)</h4>
      </div>
      <div className="triggered-alerts-list">
        {triggeredAlerts.map((result, index) => (
          <div key={index} className="triggered-alert-item">
            <div className="alert-name">{result.condition.name}</div>
            <div className="alert-message">{result.message}</div>
            <div className="alert-severity">
              {result.condition.target === 'sentiment' && result.condition.targetValue === 'ネガティブ' 
                ? '⚠️ 高' 
                : '⚠️ 中'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertChecker;
