import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import { ImageBackground, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function HomeScreen() {
  const router = useRouter();

  return (
    <ImageBackground 
      source={require('../assets/sexypic.jpg')} 
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <View style={styles.container}>
          <Text style={styles.title}>Welcome to the OXO Offline App</Text>

          <TouchableOpacity style={styles.button} onPress={() => router.push('/vin')}>
            <Text style={styles.buttonText}>🚗 Scan VIN</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.button, { backgroundColor: '#888' }]} onPress={() => router.push('/settings')}>
            <Text style={styles.buttonText}>⚙️ Settings</Text>
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
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 40,
    color: '#333',
    textAlign: 'center',
    textShadowColor: 'rgba(255, 255, 255, 0.8)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginVertical: 10,
    minWidth: '70%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

