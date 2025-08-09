import AsyncStorage from '@react-native-async-storage/async-storage';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function ResultNotOK() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const { component, partIndex, module } = useLocalSearchParams();

  const moduleName = module as string;
  const componentKey = component as string;
  const index = Number(partIndex);

  const [retryCount, setRetryCount] = useState<number | null>(null);
  const [pin, setPin] = useState('');
  const [showPinInput, setShowPinInput] = useState(false);
  const [pinError, setPinError] = useState('');

  const pendingKey = `${moduleName}_pending_count`;
  const notokKey = `${moduleName}_notok_count`;

  useEffect(() => {
    const loadRetries = async () => {
      const value = await AsyncStorage.getItem('retries');
      setRetryCount(value ? parseInt(value) : 0);
    };
    loadRetries();
  }, []);

  const getTotalParts = async () => {
    const cached = await AsyncStorage.getItem(`${moduleName}_components`);
    if (!cached) return 1;
    const parsed = JSON.parse(cached);
    return parsed[componentKey]?.parts?.length || 1;
  };

  const handleRetake = async () => {
    const newCount = (retryCount ?? 0) + 1;
    await AsyncStorage.setItem('retries', newCount.toString());
    router.push({
      pathname: '/reference',
      params: {
        component: componentKey,
        module: moduleName,
        partIndex: partIndex?.toString() || '0',
      },
    });
  };

  const handleBypass = () => {
    setShowPinInput(true);
    setPin('');
    setPinError('');
  };

  const verifyPin = async () => {
    if (pin === '0000') {
      setPinError('');

      const statusKey = `status_${componentKey}`;
      const statusRaw = await AsyncStorage.getItem(statusKey);
      const statusObj = statusRaw ? JSON.parse(statusRaw) : {};

      statusObj[index.toString()] = 'notok';
      statusObj.overall = 'notok'; // ✅ Force overall to notok once any part fails

      const currentNotOk = parseInt((await AsyncStorage.getItem('notok_count')) || '0');
      await AsyncStorage.setItem('notok_count', (currentNotOk + 1).toString());

      const totalParts = await getTotalParts();
      const isLastPart = index + 1 >= totalParts;

      if (isLastPart) {
        // ✅ Update module-level counts
        const pending = parseInt((await AsyncStorage.getItem(pendingKey)) || '0');
        const notok = parseInt((await AsyncStorage.getItem(notokKey)) || '0');
        await AsyncStorage.setItem(pendingKey, Math.max(pending - 1, 0).toString());
        await AsyncStorage.setItem(notokKey, (notok + 1).toString());

        // ✅ Finalize session counts
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
        Alert.alert('Bypass Validated', 'Returning to Hub...');
        router.replace({
          pathname: `/${moduleName}-hub` as
            | '/interior-hub'
            | '/exterior-hub'
            | '/loose-hub',
        });
      } else {
        Alert.alert('Bypass Validated', 'Proceeding to next part...');
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
    } else {
      setPinError('Incorrect PIN. Please try again.');
    }
  };

  if (retryCount === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.infoText}>Loading retry state...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={[styles.container, { paddingBottom: insets.bottom + 60 }]}
        keyboardShouldPersistTaps="handled"
      >
        {/* 👇 No need for extra wrapper View here, your layout is already vertically centered */}
        {retryCount === 0 ? (
          <>
            <Image source={require('../assets/retry.png')} style={styles.statusImage} resizeMode="contain" />
            <Text style={styles.retryText}>Retake the Image</Text>
          </>
        ) : (
          <>
            <Image source={require('../assets/notok.png')} style={styles.statusImage} resizeMode="contain" />
            <Text style={styles.errorText}>❌ Image did not match the reference.</Text>
          </>
        )}

        <Text style={styles.infoText}>
          {retryCount === 0
            ? 'Take a better image, more accurate to the reference image.'
            : 'You may retry again or bypass with a PIN.'}
        </Text>

        <TouchableOpacity style={styles.buttonRed} onPress={handleRetake}>
          <Text style={styles.buttonText}>Retake Image</Text>
        </TouchableOpacity>

        {retryCount >= 1 && !showPinInput && (
          <TouchableOpacity style={styles.buttonGray} onPress={handleBypass}>
            <Text style={styles.buttonText}>Bypass with PIN</Text>
          </TouchableOpacity>
        )}

        {showPinInput && (
          <View style={[styles.pinBox, { marginBottom: insets.bottom + 40 }]}>
            <TextInput
              style={styles.input}
              placeholder="Enter PIN"
              secureTextEntry
              keyboardType="numeric"
              value={pin}
              onChangeText={setPin}
            />
            <TouchableOpacity style={styles.buttonGray} onPress={verifyPin}>
              <Text style={styles.buttonText}>Submit</Text>
            </TouchableOpacity>
            {pinError !== '' && <Text style={styles.errorPin}>{pinError}</Text>}
          </View>
        )}

      </ScrollView>
    </KeyboardAvoidingView>

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
  statusImage: {
    width: 200,
    height: 200,
    marginBottom: 30,
    borderRadius: 100,
  },
  errorText: {
    fontSize: 20,
    fontWeight: '600',
    color: 'red',
    marginBottom: 16,
  },
  retryText: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 16,
  },
  infoText: {
    fontSize: 16,
    marginBottom: 30,
    textAlign: 'center',
  },
  buttonRed: {
    backgroundColor: '#FF3B30',
    padding: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
    marginBottom: 10,
  },
  buttonGray: {
    backgroundColor: '#8E8E93',
    padding: 12,
    paddingHorizontal: 30,
    borderRadius: 8,
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
  },
  pinBox: {
    alignItems: 'center',
    marginTop: 20,
    width: '100%',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 10,
    width: 200,
    fontSize: 16,
    marginBottom: 10,
  },
  errorPin: {
    color: 'red',
    fontSize: 14,
    marginTop: 5,
  },
});
