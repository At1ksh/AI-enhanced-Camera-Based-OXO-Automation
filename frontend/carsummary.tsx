import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { getBackendBaseURL } from '../utils/api';

interface CarOverall {
  main_image: string;
  model_name: string;
  variant_name: string;
  case_spec: string;
  vin: string;
  full_vin: string;
  engine_number: string;
  total_interior: number;
  total_exterior: number;
  total_loose: number;
}

export default function CarSummary() {
  const router = useRouter();
  const insets = useSafeAreaInsets(); 
  const [carData, setCarData] = useState<CarOverall | null>(null);
  const [loading, setLoading] = useState(true);
  const retryPost = async (url: string, data: any, headers = {}, maxAttempts = 4) => {
    let response;
    for (let i = 0; i < maxAttempts; i++) {
      try {
        response = await axios.post(url, data, {
          headers,
          timeout: 10000,
        });
        return response;
      } catch (err: any) {
        console.warn(`❌ Retry ${i + 1} failed: ${err.message}`);
        if (i === maxAttempts - 1) throw err;
        await new Promise(res => setTimeout(res, 1000));
      }
    }
  };
  useEffect(() => {
    const loadCarData = async () => {
      try {
        const storedData = await AsyncStorage.getItem('car_overall');
        if (storedData) {
          const parsed: CarOverall = JSON.parse(storedData);
          setCarData(parsed);

          // ✅ After loading car data, call backend to initialize audit folder
          await initializeAudit(parsed);
        }
      } catch (error) {
        console.error('❌ Failed to load car_overall:', error);
      } finally {
        setLoading(false);
      }
    };

    const initializeAudit = async (car: CarOverall) => {
      try {
        const personName = await AsyncStorage.getItem('person_name');
        const personPno = await AsyncStorage.getItem('person_pno');
        const personDepartment = await AsyncStorage.getItem('person_department');

        const interiorRaw = await AsyncStorage.getItem('interior_components');
        const exteriorRaw = await AsyncStorage.getItem('exterior_components');
        const looseRaw = await AsyncStorage.getItem('loose_components');

        const interiorComponents = interiorRaw
          ? Object.values(JSON.parse(interiorRaw)).map((c: any) => c.name)
          : [];
        const exteriorComponents = exteriorRaw
          ? Object.values(JSON.parse(exteriorRaw)).map((c: any) => c.name)
          : [];
        const looseComponents = looseRaw
          ? Object.values(JSON.parse(looseRaw)).map((c: any) => c.name)
          : []; 

        const formData = new FormData();
        formData.append('full_vin', car.full_vin);
        formData.append('short_vin', car.vin);
        formData.append('case_spec', car.case_spec);
        formData.append('variant', car.variant_name);
        formData.append('engine_number', car.engine_number);
        formData.append('person_name', personName || 'Unknown');
        formData.append('person_pno', personPno || 'Unknown');
        formData.append('person_department', personDepartment || 'Unknown');
        formData.append(
          'components',
          JSON.stringify({
            interior: interiorComponents,
            exterior: exteriorComponents,
            loose: looseComponents,
          })
        );

        const baseURL= await getBackendBaseURL();
        const res = await retryPost(`${baseURL}/initialize_audit`, formData, {
          'Content-Type': 'multipart/form-data'
        });

        if (res && res.data?.status !== 'success') {
          console.warn('⚠️ Audit initialization returned non-success:', res.data);
        }
      } catch (err: any) {
        console.error('❌ Audit initialization failed:', err.message);
        Alert.alert('Error', 'Could not initialize audit folder.');
      }
    };

    loadCarData();
  }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
  <ImageBackground
    source={require('../assets/sexypic.jpg')}
    style={styles.backgroundImage}
    resizeMode="cover"
  >
    <BlurView intensity={80} style={styles.blurContainer}>
      {/* ✅ Scrollable Content */}
      <ScrollView contentContainerStyle={[styles.container,{paddingBottom: 100}]}>
        {/* Car Image */}
        {carData?.main_image ? (
          <Image
            source={{ uri: carData.main_image }}
            style={styles.carImage}
            resizeMode="contain"
          />
        ) : (
          <Image
            source={require('../assets/model.jpg')}
            style={styles.carImage}
            resizeMode="contain"
          />
        )}
        <Text style={styles.imageCaption}>
          {carData ? `Model Image - ${carData.model_name}` : 'Representative image'}
        </Text>

        {/* Car Info Card */}
        <View style={styles.infoCard}>
          <Text style={styles.label}>Full VIN Number</Text>
          <Text style={styles.value}>{carData?.full_vin || 'N/A'}</Text>

          <Text style={styles.label}>Short VIN (Last 6)</Text>
          <Text style={styles.value}>{carData?.vin || 'N/A'}</Text>

          <Text style={styles.label}>Case Specification</Text>
          <Text style={styles.value}>{carData?.case_spec || 'N/A'}</Text>

          <Text style={styles.label}>Model</Text>
          <Text style={styles.value}>{carData?.model_name || 'N/A'}</Text>

          <Text style={styles.label}>Variant</Text>
          <Text style={styles.value}>{carData?.variant_name || 'N/A'}</Text>

          <Text style={styles.label}>Engine Number</Text>
          <Text style={styles.value}>{carData?.engine_number || 'N/A'}</Text>

          <Text style={styles.label}>Total Components</Text>
          <Text style={styles.value}>
            Interior: {carData?.total_interior || 0} | Exterior: {carData?.total_exterior || 0} | Loose: {carData?.total_loose || 0}
          </Text>
        </View>
      </ScrollView>

      {/* ✅ Fixed bottom button container */}
      <View style={[styles.fixedButtonContainer, { paddingBottom: insets.bottom + 12 }]}>
        <TouchableOpacity
          style={styles.proceedButton}
          onPress={() => router.push('/mainhub')}
        >
          <AntDesign name="arrowright" size={22} color="#fff" />
          <Text style={styles.proceedText}>Proceed to Main Hub</Text>
        </TouchableOpacity>
      </View>
    </BlurView>
  </ImageBackground>
);

}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  blurContainer: {
    flex: 1,
  },
  fixedButtonContainer: {
    width: '100%',
    paddingHorizontal: 20,
    paddingTop: 10,
    backgroundColor: 'transparent',  // or rgba(255,255,255,0.1) if you want semi-blur feel
    position: 'absolute',
    bottom: 0,
    alignItems: 'center',
  },

  container: {
    padding: 20,
    alignItems: 'center',
  },
  carImage: {
    width: '90%',
    height: 180,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#fff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  imageCaption: {
    fontSize: 12,
    color: '#555',
    marginBottom: 20,
    fontStyle: 'italic',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    textAlign: 'center',
  },
  infoCard: {
    width: '95%',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 14,
    padding: 20,
    elevation: 6,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
    marginBottom: 30,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 12,
  },
  value: {
    fontSize: 16,
    color: '#111',
    marginBottom: 6,
    borderBottomWidth: 0.5,
    borderBottomColor: '#ccc',
    paddingBottom: 4,
  },
  proceedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 36,
    borderRadius: 50,
    width: '80%',
    alignSelf: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
  },
  proceedText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
    marginLeft: 8,
  },

});
