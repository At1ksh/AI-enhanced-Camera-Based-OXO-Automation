import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  ImageBackground,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

interface CarOverall {
  full_vin: string;
  model_name: string;
  variant_name: string;
}

export default function FinishScreen() {
  const router = useRouter();
  const [personName, setPersonName] = useState('Technician');
  const [fullVin, setFullVin] = useState('N/A');
  const [model, setModel] = useState('N/A');
  const [variant, setVariant] = useState('N/A');

  useEffect(() => {
    const loadDataAndClear = async () => {
      try {
        // ✅ Load Personal Name
        const name = (await AsyncStorage.getItem('person_name')) || 'Technician';
        setPersonName(name);

        // ✅ Load Car Info
        const carRaw = await AsyncStorage.getItem('car_overall');
        if (carRaw) {
          const car: CarOverall = JSON.parse(carRaw);
          setFullVin(car.full_vin || 'N/A');
          setModel(car.model_name || 'N/A');
          setVariant(car.variant_name || 'N/A');
        }

        // ✅ Clear all session-related AsyncStorage keys after 1s delay (optional)
        setTimeout(async () => {
          await AsyncStorage.clear();
          console.log('✅ All AsyncStorage session data cleared after finishing.');
        }, 1500);
      } catch (e) {
        console.error('❌ Error loading or clearing data:', e);
      }
    };

    loadDataAndClear();
  }, []);

  const handleGoHome = () => {
    router.replace('/'); // ✅ Go back to home or login
  };

  return (
    <ImageBackground
      source={require('../assets/welcome-bg2.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <View style={styles.container}>
          <Text style={styles.thankYou}>🎉 Thank You, {personName}!</Text>
          <Text style={styles.infoText}>
            ✅ Scanning Completed for VIN: {fullVin}
          </Text>
          <Text style={styles.infoText}>🚗 Model: {model}</Text>
          <Text style={styles.infoText}>🛠 Variant: {variant}</Text>

          <TouchableOpacity style={styles.finishButton} onPress={handleGoHome}>
            <Text style={styles.finishButtonText}>Finish & Go Home</Text>
          </TouchableOpacity>
        </View>
      </BlurView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  backgroundImage: { flex: 1 },
  blurContainer: { flex: 1 },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  thankYou: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 20,
    textAlign: 'center',
  },
  infoText: {
    fontSize: 18,
    color: '#333',
    marginBottom: 10,
    textAlign: 'center',
  },
  finishButton: {
    marginTop: 30,
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 8,
    elevation: 5,
  },
  finishButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
