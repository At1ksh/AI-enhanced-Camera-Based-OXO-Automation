import { Stack } from 'expo-router';

export default function Layout() {
  return (
    <Stack
      initialRouteName="index"
      screenOptions={{
        headerShown: false, // 👈 This hides all headers including back arrows
      }}
    >
      <Stack.Screen name="index" />
      <Stack.Screen name="vin" />
      <Stack.Screen name="carsummary" />
      <Stack.Screen name="mainhub" />
      <Stack.Screen name="exterior-hub" />
      <Stack.Screen name="interior-hub" />
      <Stack.Screen name="instruction" />
      <Stack.Screen name="reference" />
      <Stack.Screen name="rectify" />
      <Stack.Screen name="processing" />
    </Stack>
  );
}