import AsyncStorage from '@react-native-async-storage/async-storage';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

interface ComponentEntry {
  name: string;
  image: string;
  parts: string[];
  referenceImages: string[];
}

export default function ResultOK() {
  const router = useRouter();
  const { component, partIndex, module } = useLocalSearchParams();

  const componentKey = component as string;
  const moduleName = module as string;
  const index = Number(partIndex);

  const [totalParts, setTotalParts] = useState(1);

  // ✅ Load totalParts dynamically from AsyncStorage
  useEffect(() => {
    const loadTotalParts = async () => {
      try {
        const compKey = `${moduleName}_components`;
        const cached = await AsyncStorage.getItem(compKey);
        const parsed: Record<string, ComponentEntry> = cached ? JSON.parse(cached) : {};
        const selected = parsed[componentKey];

        if (selected && selected.parts) {
          setTotalParts(selected.parts.length);
        }
      } catch (err) {
        console.error('❌ Failed to load total parts:', err);
      }
    };

    loadTotalParts();
  }, [moduleName, componentKey]);

  const handleProceed = async () => {
    const statusKey = `status_${componentKey}`;
    const statusRaw = await AsyncStorage.getItem(statusKey);
    const statusObj = statusRaw ? JSON.parse(statusRaw) : {};

    // ✅ Mark current part as OK
    statusObj[index.toString()] = 'ok';

    // Update per-session OK count
    const existingOk = parseInt((await AsyncStorage.getItem('ok_count')) || '0');
    await AsyncStorage.setItem('ok_count', (existingOk + 1).toString());

    const isLastPart = index + 1 >= totalParts;

    if (isLastPart) {
      const pendingKey = `${moduleName}_pending_count`;
      const okKey = `${moduleName}_ok_count`;
      const notokKey = `${moduleName}_notok_count`;

      if (statusObj.overall === 'pending') {
        statusObj.overall = 'ok';

        const pending = parseInt((await AsyncStorage.getItem(pendingKey)) || '0');
        const ok = parseInt((await AsyncStorage.getItem(okKey)) || '0');
        await AsyncStorage.setItem(pendingKey, (pending - 1).toString());
        await AsyncStorage.setItem(okKey, (ok + 1).toString());
      } else if (statusObj.overall === 'notok') {
        const pending = parseInt((await AsyncStorage.getItem(pendingKey)) || '0');
        const notok = parseInt((await AsyncStorage.getItem(notokKey)) || '0');
        await AsyncStorage.setItem(pendingKey, (pending - 1).toString());
        await AsyncStorage.setItem(notokKey, (notok + 1).toString());
      }

      // Save session ok/notok count to component
      const sessionOk = parseInt((await AsyncStorage.getItem('ok_count')) || '0');
      const sessionNotOk = parseInt((await AsyncStorage.getItem('notok_count')) || '0');
      await AsyncStorage.setItem(
        `${componentKey}_result_count`,
        JSON.stringify({ ok: sessionOk, notok: sessionNotOk })
      );

      await AsyncStorage.setItem('ok_count', '0');
      await AsyncStorage.setItem('notok_count', '0');
    }

    await AsyncStorage.setItem(statusKey, JSON.stringify(statusObj));

    if (isLastPart) {
      switch (moduleName) {
        case 'interior':
          router.replace('/interior-hub');
          break;
        case 'exterior':
          router.replace('/exterior-hub');
          break;
        case 'loose':
          router.replace('/loose-hub');
          break;
      }
    } else {
      await AsyncStorage.setItem('retries', '0');
      router.replace({
        pathname: '/reference',
        params: {
          component: componentKey,
          module: moduleName,
          partIndex: (index + 1).toString(),
        },
      });
    }
  };

  return (
    <View style={styles.container}>
      <Image
        source={require('../assets/ok.png')}
        style={styles.successImage}
        resizeMode="contain"
      />
      <Text style={styles.successText}>✅ Component Verified Successfully!</Text>
      <TouchableOpacity style={styles.button} onPress={handleProceed}>
        <Text style={styles.buttonText}>Proceed</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
    paddingTop: 50,
  },
  successImage: {
    width: 200,
    height: 200,
    marginBottom: 30,
    borderRadius: 100,
  },
  successText: { fontSize: 20, fontWeight: '600', color: 'green', marginBottom: 30 },
  button: { backgroundColor: '#007AFF', paddingVertical: 12, paddingHorizontal: 30, borderRadius: 8 },
  buttonText: { color: '#fff', fontSize: 16 },
});
