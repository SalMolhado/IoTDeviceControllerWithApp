import React, { useEffect, useState, useContext } from 'react';
import { ScrollView, View, Button, StyleSheet } from 'react-native';
import { Table, Row, Rows } from 'react-native-table-component';
import GatewayAddress from './GatewayAddress';

// tela aonde visualizamos os registros
const SensorDataScreen = () => {
  // endereços
  const gatewayAddress = useContext(GatewayAddress);
  const loggingDataAddress = `${gatewayAddress}/logging/data`;

  // estados
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  // pega registros
  const fetchData = async (retryCount = 3) => {
    setRefreshing(true);
    try {
      const response = await fetch(loggingDataAddress, { method: 'GET' });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      console.log(response.status);
      const json = await response.json();
      setData(json);
    } catch (error) {
      console.error(`Fetch operation failed: ${error.message}`);
      if (retryCount > 0) {
        console.log(`Retrying... Attempts remaining: ${retryCount}`);
        fetchData(retryCount - 1);
      }
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [gatewayAddress]);

  // atualiza
  const handleRefresh = () => {
    if (!refreshing) {
      fetchData();
    }
  };

  // cabeçalho e linhas da tabela
  const tableHead = ['Trigger Activated', 'Temperature', 'Timestamp'];
  const tableData = data.map((item) => [
    item.trigger_activated.toString(),
    item.temperature.toString(),
    item.timestamp.toString(),
  ]);

  return (
    <View style={styles.container}>
      <ScrollView vertical={true}>
        <View style={styles.content}>
          <Table borderStyle={{ borderWidth: 1, borderColor: '#C1C0B9' }}>
            <Row
              data={tableHead}
              style={{ height: 50, backgroundColor: '#f1f8ff' }}
              textStyle={{ margin: 6 }}
            />
            <Rows data={tableData} textStyle={{ margin: 6 }} />
          </Table>
          <Button title="Refresh" onPress={handleRefresh} />
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    marginBottom: 5,
  },
});

export default SensorDataScreen;
