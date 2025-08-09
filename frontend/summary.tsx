import { getBackendBaseURL } from '@/utils/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import axios from 'axios';
import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import React, { useCallback, useState } from 'react';
import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

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

export default function SummaryScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [counts, setCounts] = useState({
    interior: { pending: 0, ok: 0, notok: 0 },
    exterior: { pending: 0, ok: 0, notok: 0 },
    loose: { pending: 0, ok: 0, notok: 0 },
  });

  const [expandedSections, setExpandedSections] = useState({
    personal: false,
    interior: false,
    exterior: false,
    loose: false,
  });

  const [personalInfo, setPersonalInfo] = useState({
    person_name: '',
    person_pno: '',
    person_department: '',
  });

  const [carInfo, setCarInfo] = useState<CarOverall | null>(null);

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  useFocusEffect(
    useCallback(() => {
      const loadData = async () => {
        // ✅ Load Counts
        const get = async (key: string) => parseInt((await AsyncStorage.getItem(key)) ?? '0');

        const interior = {
          pending: await get('interior_pending_count'),
          ok: await get('interior_ok_count'),
          notok: await get('interior_notok_count'),
        };
        const exterior = {
          pending: await get('exterior_pending_count'),
          ok: await get('exterior_ok_count'),
          notok: await get('exterior_notok_count'),
        };
        const loose = {
          pending: await get('loose_pending_count'),
          ok: await get('loose_ok_count'),
          notok: await get('loose_notok_count'),
        };

        setCounts({ interior, exterior, loose });

        // ✅ Load Personal Info
        const person_name = (await AsyncStorage.getItem('person_name')) || 'N/A';
        const person_pno = (await AsyncStorage.getItem('person_pno')) || 'N/A';
        const person_department = (await AsyncStorage.getItem('person_department')) || 'N/A';
        setPersonalInfo({ person_name, person_pno, person_department });

        // ✅ Load Car Info
        const storedCar = await AsyncStorage.getItem('car_overall');
        if (storedCar) {
          setCarInfo(JSON.parse(storedCar));
        }
      };

      loadData();
    }, [])
  );

  const total = {
    ok: counts.interior.ok + counts.exterior.ok + counts.loose.ok,
    notok: counts.interior.notok + counts.exterior.notok + counts.loose.notok,
    pending: counts.interior.pending + counts.exterior.pending + counts.loose.pending,
  };

  const finalizeAudit = async () => {
    try {
      const carOverallRaw = await AsyncStorage.getItem("car_overall");
      if (!carOverallRaw) {
        alert("Car details not found!");
        return;
      }
      const carOverall = JSON.parse(carOverallRaw);

      // ✅ Collect all component statuses (CORRECTED)
      const componentStatuses: { [key: string]: { [key: string]: string } } = {};

      // Get component configurations
      const interiorConfig = JSON.parse(await AsyncStorage.getItem('interior_components') || '{}');
      const exteriorConfig = JSON.parse(await AsyncStorage.getItem('exterior_components') || '{}');
      const looseConfig = JSON.parse(await AsyncStorage.getItem('loose_components') || '{}');

      const configs = {
        interior: interiorConfig,
        exterior: exteriorConfig,
        loose: looseConfig
      };

      for (const [categoryName, config] of Object.entries(configs)) {
        componentStatuses[categoryName] = {};
        
        for (const [sysname, componentData] of Object.entries(config as any)) {
          const statusRaw = await AsyncStorage.getItem(`status_${sysname}`);
          if (statusRaw) {
            const statusObj = JSON.parse(statusRaw);
            // Use overall status or derive from individual part statuses
            componentStatuses[categoryName][sysname] = statusObj.overall || 'pending';

          }
        }
      }

      const formData = new FormData();
      formData.append("full_vin", carOverall.full_vin);
      formData.append("total_ok", total.ok.toString());
      formData.append("total_notok", total.notok.toString());
      formData.append("total_pending", total.pending.toString());
      
      // ✅ Add detailed component statuses
      formData.append("component_statuses", JSON.stringify(componentStatuses));

      const baseURL = await getBackendBaseURL();
      const res = await axios.post(`${baseURL}/finalize_audit`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 20000,
      });

      if (res.data.status === "success") {
        alert(`✅ Audit Finalized: ${res.data.final_verdict}`);
        router.replace('/finish'); // Or a thank-you page
      } else {
        alert(`❌ Failed: ${res.data.message}`);
      }
    } catch (e: any) {
      alert(`❌ Error finalizing audit: ${e.message}`);
    }
  };

  return (
    <ImageBackground
      source={require('../assets/sexypic.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <View style={styles.container}>
          <ScrollView
            contentContainerStyle={[styles.scrollContainer, { paddingBottom: insets.bottom + 150 }]}
          >
            {/* Summary Header Box */}
            <View style={styles.summaryHeader}>
              <Text style={styles.summaryTitle}>📊 Total Summary</Text>
              <View style={styles.summaryStats}>
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>{total.ok}</Text>
                  <Text style={styles.statLabel}>✅ OK</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>{total.notok}</Text>
                  <Text style={styles.statLabel}>❌ NOT OK</Text>
                </View>
                <View style={styles.statItem}>
                  <Text style={styles.statNumber}>{total.pending}</Text>
                  <Text style={styles.statLabel}>🕓 Pending</Text>
                </View>
              </View>
            </View>

            {/* Personal Information Dropdown */}
            <View style={styles.dropdownContainer}>
              <TouchableOpacity
                style={styles.dropdownHeader}
                onPress={() => toggleSection('personal')}
              >
                <Text style={styles.dropdownTitle}>👤 Personal & Car Information</Text>
                <Text style={styles.dropdownArrow}>
                  {expandedSections.personal ? '▼' : '▶'}
                </Text>
              </TouchableOpacity>
              {expandedSections.personal && (
                <View style={styles.dropdownContent}>
                  <Text style={styles.infoText}>👤 Name: {personalInfo.person_name}</Text>
                  <Text style={styles.infoText}>🆔 PNo: {personalInfo.person_pno}</Text>
                  <Text style={styles.infoText}>🏢 Department: {personalInfo.person_department}</Text>
                  {carInfo && (
                    <>
                      <Text style={styles.infoText}>🚗 Full VIN: {carInfo.full_vin}</Text>
                      <Text style={styles.infoText}>🔖 Short VIN: {carInfo.vin}</Text>
                      <Text style={styles.infoText}>🛠 Case Spec: {carInfo.case_spec}</Text>
                      <Text style={styles.infoText}>📌 Model: {carInfo.model_name}</Text>
                      <Text style={styles.infoText}>🏷 Variant: {carInfo.variant_name}</Text>
                      <Text style={styles.infoText}>⚙ Engine: {carInfo.engine_number}</Text>
                      <Text style={styles.infoText}>
                        Total Components → Interior: {carInfo.total_interior} | Exterior: {carInfo.total_exterior} | Loose: {carInfo.total_loose}
                      </Text>
                    </>
                  )}
                </View>
              )}
            </View>

            {/* Interior Summary */}
            <View style={styles.dropdownContainer}>
              <TouchableOpacity
                style={styles.dropdownHeader}
                onPress={() => toggleSection('interior')}
              >
                <Text style={styles.dropdownTitle}>🏠 Interior Summary</Text>
                <Text style={styles.dropdownArrow}>
                  {expandedSections.interior ? '▼' : '▶'}
                </Text>
              </TouchableOpacity>
              {expandedSections.interior && (
                <View style={styles.dropdownContent}>
                  <Text style={styles.cardText}>✔ OK: {counts.interior.ok}</Text>
                  <Text style={styles.cardText}>❌ NOT OK: {counts.interior.notok}</Text>
                  <Text style={styles.cardText}>🕓 Pending: {counts.interior.pending}</Text>
                </View>
              )}
            </View>

            {/* Exterior Summary */}
            <View style={styles.dropdownContainer}>
              <TouchableOpacity
                style={styles.dropdownHeader}
                onPress={() => toggleSection('exterior')}
              >
                <Text style={styles.dropdownTitle}>🚗 Exterior Summary</Text>
                <Text style={styles.dropdownArrow}>
                  {expandedSections.exterior ? '▼' : '▶'}
                </Text>
              </TouchableOpacity>
              {expandedSections.exterior && (
                <View style={styles.dropdownContent}>
                  <Text style={styles.cardText}>✔ OK: {counts.exterior.ok}</Text>
                  <Text style={styles.cardText}>❌ NOT OK: {counts.exterior.notok}</Text>
                  <Text style={styles.cardText}>🕓 Pending: {counts.exterior.pending}</Text>
                </View>
              )}
            </View>

            {/* Loose Car Points */}
            <View style={styles.dropdownContainer}>
              <TouchableOpacity
                style={styles.dropdownHeader}
                onPress={() => toggleSection('loose')}
              >
                <Text style={styles.dropdownTitle}>🔧 Loose Car Points</Text>
                <Text style={styles.dropdownArrow}>
                  {expandedSections.loose ? '▼' : '▶'}
                </Text>
              </TouchableOpacity>
              {expandedSections.loose && (
                <View style={styles.dropdownContent}>
                  <Text style={styles.cardText}>✔ OK: {counts.loose.ok}</Text>
                  <Text style={styles.cardText}>❌ NOT OK: {counts.loose.notok}</Text>
                  <Text style={styles.cardText}>🕓 Pending: {counts.loose.pending}</Text>
                </View>
              )}
            </View>
          </ScrollView>

          {/* Sticky Bottom Buttons */}
          <View style={[styles.bottomButtonContainer, { paddingBottom: insets.bottom + 20 }]}>
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => router.replace('/mainhub')}
            >
              <Text style={styles.backText}>← Go Back</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.submitButton}
              onPress={finalizeAudit}
            >
              <Text style={styles.submitText}>Submit ✅</Text>
            </TouchableOpacity>
          </View>
        </View>
      </BlurView>
    </ImageBackground>
  );
}



const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
  },
  blurContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  scrollContainer: {
    padding: 20,
    paddingTop: 60, // Top padding for safe area
    paddingBottom: 100, // Extra bottom padding for sticky buttons
    alignItems: 'center',
  },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 10 },
  subtitle: { fontSize: 16, color: '#666', marginBottom: 20 },

  // Summary Header Styles
  summaryHeader: {
    width: '100%',
    backgroundColor: '#1e88e5',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  summaryTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 15,
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  statLabel: {
    fontSize: 12,
    color: '#e3f2fd',
    marginTop: 4,
  },

  // Dropdown Styles
  dropdownContainer: {
    width: '100%',
    marginBottom: 12,
    borderRadius: 12,
    backgroundColor: '#fff',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  dropdownHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderTopLeftRadius: 12,
    borderTopRightRadius: 12,
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
  },
  dropdownTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  dropdownArrow: {
    fontSize: 16,
    color: '#666',
    fontWeight: 'bold',
  },
  dropdownContent: {
    padding: 16,
    paddingTop: 8,
    backgroundColor: '#fff',
    borderBottomLeftRadius: 12,
    borderBottomRightRadius: 12,
  },

  infoText: {
    fontSize: 16,
    marginBottom: 8,
    color: '#555',
  },
  cardText: { 
    fontSize: 16, 
    marginBottom: 8,
    color: '#555',
  },

  bottomButtonContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    //backgroundColor: '#fff',
    //borderTopWidth: 1,
    //borderTopColor: '#e0e0e0',
    //elevation: 5,
    //shadowColor: '#000',
    //shadowOffset: { width: 0, height: -2 },
    //shadowOpacity: 0.1,
    //shadowRadius: 4,
  },

  submitButton: {
    backgroundColor: '#007AFF', // Blue color
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  submitText: { 
    color: '#fff', 
    fontSize: 16, 
    fontWeight: '600' 
  },

  backButton: {
    backgroundColor: '#28a745', // Green color
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  backText: { 
    color: '#fff', 
    fontSize: 16,
    fontWeight: '600'
  },
});
