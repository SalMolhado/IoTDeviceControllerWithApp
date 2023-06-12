import React, { useContext, useState, useEffect } from 'react';
import { View, Text } from 'react-native';
import { Slider } from 'react-native-elements';
import GatewayAddress from './GatewayAddress';

// tela aonde atualizamos os parametros
const SelectionScreen = () => {
  // endereços
  const gatewayAddress = useContext(GatewayAddress);
  const controlConditionAddress = `${gatewayAddress}/control/condition`;
  const controlAngleAddress = `${gatewayAddress}/control/angle`;

  // estados inciais dos sliders
  const [initialAngle, setInitialAngle] = useState(0);
  const [initialCondition, setInitialCondition] = useState(0);

  useEffect(() => {
    // pega valores atuais para posicionar os sliders
    fetch(`${controlAngleAddress}`, { method: 'GET' })
      .then((response) => response.text())
      .then((text) => setInitialAngle(parseInt(text)))
      .catch((error) =>
        console.error(`Fetch operation failed: ${error.message}`)
      );

    fetch(`${controlConditionAddress}`, { method: 'GET' })
      .then((response) => response.text())
      .then((text) => setInitialCondition(parseFloat(text)))
      .catch((error) =>
        console.error(`Fetch operation failed: ${error.message}`)
      );
  }, []);

  // atualiza temperatura minima registrada pelo sensor para ativar o atuador
  const updateAngle = (angle) => {
    const formattedAngle = parseInt(angle);
    fetch(`${controlAngleAddress}/${formattedAngle}`, { method: 'POST' })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }
        console.log(response.status);
      })
      .catch((error) =>
        console.error(`Fetch operation failed: ${error.message}`)
      );
  };

  // atualiza angulo ao qual a hélice do atuador rotaciona
  const updateCondition = (condition) => {
    const formattedCondition = condition.toFixed(2);
    fetch(`${controlConditionAddress}/${formattedCondition}`, {
      method: 'POST',
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }
        console.log(response.status);
      })
      .catch((error) =>
        console.error(`Fetch operation failed: ${error.message}`)
      );
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 20 }}>
      <Text style={{ fontSize: 20, marginBottom: 20, textAlign: 'center' }}>
        Servo Rotation Angle
      </Text>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Text>0</Text>
        <Slider
          style={{ flex: 1 }}
          minimumValue={0}
          maximumValue={360}
          value={initialAngle}
          onValueChange={updateAngle}
        />
        <Text>360</Text>
      </View>

      <Text
        style={{
          fontSize: 20,
          marginTop: 40,
          marginBottom: 20,
          textAlign: 'center',
        }}>
        Temperature Trigger
      </Text>
      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Text>-50.0</Text>
        <Slider
          style={{ flex: 1 }}
          minimumValue={-50.0}
          maximumValue={100.0}
          value={initialCondition}
          onValueChange={updateCondition}
        />
        <Text>100.0</Text>
      </View>
    </View>
  );
};

export default SelectionScreen;
