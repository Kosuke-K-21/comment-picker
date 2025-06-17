import React, { useState } from 'react';

export interface AlertCondition {
  id: string;
  name: string;
  type: 'count' | 'percentage';
  target: 'sentiment' | 'category' | 'importance';
  targetValue?: string;
  operator: 'gte' | 'lte' | 'eq';
  threshold: number;
  enabled: boolean;
}

interface AlertSettingsProps {
  conditions: AlertCondition[];
  onConditionsChange: (conditions: AlertCondition[]) => void;
  statistics?: any;
}

const AlertSettings: React.FC<AlertSettingsProps> = ({ 
  conditions, 
  onConditionsChange, 
  statistics 
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCondition, setNewCondition] = useState<Partial<AlertCondition>>({
    name: '',
    type: 'percentage',
    target: 'sentiment',
    targetValue: 'ネガティブ',
    operator: 'gte',
    threshold: 30,
    enabled: true
  });

  const addCondition = () => {
    if (!newCondition.name) return;
    
    const condition: AlertCondition = {
      id: Date.now().toString(),
      name: newCondition.name!,
      type: newCondition.type!,
      target: newCondition.target!,
      targetValue: newCondition.targetValue,
      operator: newCondition.operator!,
      threshold: newCondition.threshold!,
      enabled: newCondition.enabled!
    };
    
    onConditionsChange([...conditions, condition]);
    setNewCondition({
      name: '',
      type: 'percentage',
      target: 'sentiment',
      targetValue: 'ネガティブ',
      operator: 'gte',
      threshold: 30,
      enabled: true
    });
    setShowAddForm(false);
  };

  const removeCondition = (id: string) => {
    onConditionsChange(conditions.filter(c => c.id !== id));
  };

  const toggleCondition = (id: string) => {
    onConditionsChange(conditions.map(c => 
      c.id === id ? { ...c, enabled: !c.enabled } : c
    ));
  };

  const getTargetOptions = (target: string) => {
    switch (target) {
      case 'sentiment':
        return ['ポジティブ', '中立', 'ネガティブ'];
      case 'category':
        return ['講義内容', '講義資料', '運営', 'その他'];
      case 'importance':
        return ['高', '中', '低'];
      default:
        return [];
    }
  };

  const getOperatorText = (operator: string) => {
    switch (operator) {
      case 'gte': return '以上';
      case 'lte': return '以下';
      case 'eq': return '等しい';
      default: return '';
    }
  };

  return (
    <div className="alert-settings">
      <div className="alert-settings-header">
        <h4>⚠️ アラート設定</h4>
        <button 
          onClick={() => setShowAddForm(!showAddForm)}
          className="add-alert-btn"
        >
          {showAddForm ? '✕ キャンセル' : '➕ アラート追加'}
        </button>
      </div>

      {showAddForm && (
        <div className="add-alert-form">
          <div className="form-row">
            <label>アラート名:</label>
            <input
              type="text"
              value={newCondition.name || ''}
              onChange={(e) => setNewCondition({...newCondition, name: e.target.value})}
              placeholder="例: ネガティブコメント多数"
            />
          </div>
          
          <div className="form-row">
            <label>条件タイプ:</label>
            <select
              value={newCondition.type}
              onChange={(e) => setNewCondition({...newCondition, type: e.target.value as 'count' | 'percentage'})}
            >
              <option value="count">件数</option>
              <option value="percentage">割合(%)</option>
            </select>
          </div>

          <div className="form-row">
            <label>対象:</label>
            <select
              value={newCondition.target}
              onChange={(e) => {
                const target = e.target.value as 'sentiment' | 'category' | 'importance';
                setNewCondition({
                  ...newCondition, 
                  target,
                  targetValue: getTargetOptions(target)[0]
                });
              }}
            >
              <option value="sentiment">感情</option>
              <option value="category">カテゴリ</option>
              <option value="importance">重要度</option>
            </select>
          </div>

          <div className="form-row">
            <label>値:</label>
            <select
              value={newCondition.targetValue}
              onChange={(e) => setNewCondition({...newCondition, targetValue: e.target.value})}
            >
              {getTargetOptions(newCondition.target!).map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label>条件:</label>
            <select
              value={newCondition.operator}
              onChange={(e) => setNewCondition({...newCondition, operator: e.target.value as 'gte' | 'lte' | 'eq'})}
            >
              <option value="gte">以上</option>
              <option value="lte">以下</option>
              <option value="eq">等しい</option>
            </select>
          </div>

          <div className="form-row">
            <label>閾値:</label>
            <input
              type="number"
              value={newCondition.threshold}
              onChange={(e) => setNewCondition({...newCondition, threshold: Number(e.target.value)})}
              min="0"
              max={newCondition.type === 'percentage' ? 100 : undefined}
            />
            {newCondition.type === 'percentage' && <span>%</span>}
            {newCondition.type === 'count' && <span>件</span>}
          </div>

          <div className="form-actions">
            <button onClick={addCondition} className="save-btn">保存</button>
            <button onClick={() => setShowAddForm(false)} className="cancel-btn">キャンセル</button>
          </div>
        </div>
      )}

      <div className="alert-conditions-list">
        {conditions.length === 0 ? (
          <p className="no-conditions">アラート条件が設定されていません</p>
        ) : (
          conditions.map(condition => (
            <div key={condition.id} className={`alert-condition ${condition.enabled ? 'enabled' : 'disabled'}`}>
              <div className="condition-header">
                <span className="condition-name">{condition.name}</span>
                <div className="condition-actions">
                  <button
                    onClick={() => toggleCondition(condition.id)}
                    className={`toggle-btn ${condition.enabled ? 'enabled' : 'disabled'}`}
                  >
                    {condition.enabled ? '🟢' : '🔴'}
                  </button>
                  <button
                    onClick={() => removeCondition(condition.id)}
                    className="remove-btn"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <div className="condition-details">
                {condition.targetValue} が {condition.threshold}
                {condition.type === 'percentage' ? '%' : '件'} {getOperatorText(condition.operator)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertSettings;
