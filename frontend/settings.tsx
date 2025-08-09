// settings.tsx
import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function SettingsPage() {
  const [ip, setIp] = useState('');
  const [status, setStatus] = useState<'idle' | 'checking' | 'success' | 'fail'>('idle');

  useEffect(() => {
    const loadIP = async () => {
      const savedIP = await AsyncStorage.getItem('backend_ip');
      console.log("🧠 Loaded saved IP from AsyncStorage:", savedIP);
      if (savedIP) setIp(savedIP);
    };
    loadIP();
  }, []);

  const handleSaveIP = async () => {
    console.log("💾 Saving IP to AsyncStorage:", ip);
    await AsyncStorage.setItem('backend_ip', ip);
    Alert.alert('✅ Saved', `Backend IP set to:\n${ip}`);
  };

  const testConnection = async () => {
    if (!ip.trim()) {
      Alert.alert('❌ IP Address Missing', 'Please enter a valid IP address first.');
      return;
    }

    const url = `http://${ip}/health`;
    console.log("🌐 Testing connection to:", url);

    setStatus('checking');
    try {
      const res = await axios.get(url, { timeout: 4000 });
      if (res.status === 200) {
        setStatus('success');
        console.log("✅ Backend responded OK");
        Alert.alert('✅ Connected', 'Backend is reachable.');
      } else {
        setStatus('fail');
        console.warn("⚠️ Unexpected response:", res.status);
        Alert.alert('❌ Error', 'Backend returned unexpected status.');
      }
    } catch (err: any) {
      setStatus('fail');
      console.log("🛑 Axios error:", err);

      if (err.response) {
        console.log("❗ Server responded with status:", err.response.status);
        console.log("❗ Response data:", err.response.data);
        Alert.alert('❌ Error', `Server error: ${err.response.status}`);
      } else if (err.request) {
        console.log("❗ No response received:", err.request);
        Alert.alert('❌ Error', 'No response received from backend.');
      } else {
        console.log("❗ Unknown error:", err.message);
        Alert.alert('❌ Error', `Request setup failed: ${err.message}`);
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Settings</Text>

      <Text style={styles.label}>Backend IP Address:</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. 192.168.1.10:8000"
        value={ip}
        onChangeText={setIp}
      />

      <TouchableOpacity style={styles.saveButton} onPress={handleSaveIP}>
        <Text style={styles.buttonText}>💾 Save IP</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.testButton} onPress={testConnection}>
        <Text style={styles.buttonText}>🔌 Test Backend Connection</Text>
      </TouchableOpacity>

      {status === 'success' && <Text style={styles.success}>✅ Backend is reachable</Text>}
      {status === 'fail' && <Text style={styles.fail}>❌ Backend not reachable</Text>}
      {status === 'checking' && <Text style={styles.checking}>⏳ Checking...</Text>}

      <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
        <AntDesign name="arrowleft" size={20} color="#fff" />
        <Text style={styles.backText}> Go Back</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8f9fa',
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#007AFF',
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
    fontWeight: '600',
    alignSelf: 'flex-start',
    color: '#333',
  },
  input: {
    width: '100%',
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 10,
    padding: 12,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#fff',
  },
  saveButton: {
    backgroundColor: '#28a745',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 10,
    marginBottom: 16,
  },
  testButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 10,
    marginBottom: 20,
  },
  backButton: {
    marginTop: 40,
    backgroundColor: '#6c757d',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backText: {
    color: '#fff',
    fontSize: 16,
    marginLeft: 6,
    fontWeight: '600',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  success: { color: '#28a745', fontSize: 16 },
  fail: { color: '#dc3545', fontSize: 16 },
  checking: { color: '#333', fontSize: 16 },
});
