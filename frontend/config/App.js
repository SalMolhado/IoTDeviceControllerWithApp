import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import SelectionScreen from './components/SelectionScreen';
import SensorDataScreen from './components/SensorDataScreen';
import GatewayAddressProvider from './components/GatewayAddressProvider';


const Tab = createBottomTabNavigator();

const App = () => {
  return (
    <GatewayAddressProvider>
      <NavigationContainer>
        <Tab.Navigator>
          <Tab.Screen name="Selection" component={SelectionScreen} options={{ title: 'Selection' }} />
          <Tab.Screen name="Data" component={SensorDataScreen} options={{ title: 'Sensor Data' }} />
        </Tab.Navigator>
      </NavigationContainer>
    </GatewayAddressProvider>
  );
};

export default App;