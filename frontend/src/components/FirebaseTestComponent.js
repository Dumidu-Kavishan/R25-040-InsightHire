import React, { useState, useEffect } from 'react';
import { db } from '../firebase';
import { collection, query, orderBy, limit, getDocs } from 'firebase/firestore';

const FirebaseTestComponent = () => {
  const [testResult, setTestResult] = useState('Testing...');

  useEffect(() => {
    const testFirebase = async () => {
      try {
        // Test reading from hand_confidence collection
        const handRef = collection(db, 'hand_confidence');
        const q = query(handRef, orderBy('timestamp', 'desc'), limit(1));
        const snapshot = await getDocs(q);
        
        if (!snapshot.empty) {
          const data = snapshot.docs[0].data();
          setTestResult(`✅ Firebase connected! Latest hand data: ${JSON.stringify(data, null, 2)}`);
        } else {
          setTestResult('✅ Firebase connected but no hand_confidence data found');
        }
      } catch (error) {
        setTestResult(`❌ Firebase error: ${error.message}`);
      }
    };

    testFirebase();
  }, []);

  return (
    <div style={{ padding: '20px', background: '#f5f5f5', margin: '10px', borderRadius: '8px' }}>
      <h3>Firebase Connection Test</h3>
      <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap' }}>
        {testResult}
      </pre>
    </div>
  );
};

export default FirebaseTestComponent;