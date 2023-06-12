import React, { useEffect, useState } from 'react';
import GatewayAddress from './GatewayAddress';
import { ActivityIndicator, Text } from 'react-native';

// atualiza a variável que contém o gateway
const GatewayAddressProvider = ({ children }) => {
  const [myString, setMyString] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // faz a requisição do ip pela api em http://SalMolhado.pythonanywhere.com/ip
    const fetchString = async () => {
      try {
        const response = await fetch('http://SalMolhado.pythonanywhere.com/ip');
        const json = await response.json();

        // se json.value não for uma string vazia, atualiza o estado e para de tentar
        if (json.value !== '') {
          setMyString(`http://${json.value}:8000`);
          setLoading(false);
          console.log(json.value);
        } else {
          // se json.value for uma string vazia, tenta denovo após um delay
          setTimeout(fetchString, 5000);
        }
      } catch (error) {
        console.error(`Fetch operation failed: ${error.message}`);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchString();
  }, []);

  // se um erro ocorrer, mostrar mensagem de erro
  if (error) {
    return <Text>Error: {error}</Text>;
  }

  // se a informação ainda estiver carregando, mostrar indicador de carregamento
  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  // quando a informação for carregada, renderizar a children
  return (
    <GatewayAddress.Provider value={myString}>
      {children}
    </GatewayAddress.Provider>
  );
};

export default GatewayAddressProvider;
