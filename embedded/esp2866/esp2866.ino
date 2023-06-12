#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Servo.h>

// DEPENDÊNCIAS E ESPECIFICAÇÕES
// Additional boards managers URLs: http://arduino.esp8266.com/stable/package_esp8266com_index.json
// Libraries installed: Adafruit Unified Sensor 1.1.9, DHT sensor library 1.4.4
// Board: esp8266 -> LOLIN(WEMOS) D1 R2 & mini

// INSTRUÇÕES
// amarelo: D14/D4; Preto: D15/D3; Marrom: GND; Verde: GND: Laranja: 3.3V; Vermelho: 5V
// conectar notebook ao celular 

// credenciais de WiFi
const char* ssid = "nome da rede"; 
const char* password = "senha"; 

// variáveis para os endereços
char get_condition_endpoint[70];
char get_angle_endpoint[70];
char post_condition_endpoint[70];
char post_angle_endpoint[70];
char post_data_endpoint[70];

// varável para cliente
WiFiClient wifiClient;

// sensor DHT de temperatura
#define DHTPIN D2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// atuador servo motor
#define SERVO_PIN D1
Servo servo;

// variáveis para armazenar leitura de temperatura
float rawTemperature;
String formattedTemperature;

// variáveis para armazenar parametros
float condition;
int angle;

// variável para armazenar se houve ativação
bool trigger_activated;

// varáveis para comparação
String lastSentTemperature = "";
bool lastSentTriggerActivated;

void setup() {
  Serial.begin(9600);
  delay(10);

  // conectar-se à rede WiFI
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // inicializar sensor
  dht.begin();

  // inicializar atuador
  servo.attach(SERVO_PIN);
  servo.write(90);
  servo.detach();
  getIpAddress();
}


// --------------- M A I N   L O O P ----------------

void loop() {
  Serial.println("at loop's beginning");
  Serial.println();
  // ler temperatura

  rawTemperature = dht.readTemperature();

  char tempStr[6];
  dtostrf(rawTemperature, 6, 2, tempStr);
  formattedTemperature = String(tempStr);

  // atualizar parametros pelo gateway
  condition = getConditionFromServer();
  angle = getAngleFromServer();

  // temperatura atual chega no limite?
  trigger_activated = (rawTemperature >= condition);

  // se temperatura ou condição mudaram, registrar pelo gateway
  if (formattedTemperature != lastSentTemperature || trigger_activated != lastSentTriggerActivated) {
    sendPostRequest(formattedTemperature, trigger_activated);
    lastSentTemperature = formattedTemperature;
    lastSentTriggerActivated = trigger_activated;
  }

  // se temperatura atual chega ou passou o limite, acionar atuador
  if (trigger_activated) {
    servo.attach(SERVO_PIN);
    servo.write(angle);
    delay(500);
    servo.detach();
  }
  delay(2000);
}

// atualiza parametro "condition"
float getConditionFromServer() {
  // se houver conexão
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    Serial.println("get condition from server");

    http.begin(wifiClient, get_condition_endpoint);
    int httpCode = http.GET();
    Serial.println(httpCode);

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
      Serial.println();

      http.end();

      return payload.toFloat();
    }
    else {
      Serial.println("Error on HTTP request");
      return -1;
    }
  }
  else {
    Serial.println("Error in WiFi connection");
    return -1;
  }
}

// atualiza parametro "angle"
int getAngleFromServer() {
  // se houver conexão
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    Serial.println("get angle from server");

    http.begin(wifiClient, get_angle_endpoint);
    int httpCode = http.GET();
    Serial.println(httpCode);

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
      Serial.println();

      http.end();

      return payload.toInt();
    }
    else {
      Serial.println("Error on HTTP request");
      return -1;
    }
  }
  else {
    Serial.println("Error in WiFi connection");
    return -1;
  }
}

// registra um registro pelo gateway
void sendPostRequest(String temperature, bool trigger_activated) {
  // se houver conexão
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    Serial.println("registry post request to server");

    String postData;
    DynamicJsonDocument doc(1024);
    doc["temperature"] = temperature;
    doc["trigger_activated"] = trigger_activated;
    serializeJson(doc, postData);

    http.begin(wifiClient, post_data_endpoint);
    http.addHeader("Content-Type", "application/json");
    Serial.println(post_data_endpoint);

    int httpCode = http.POST(postData);
    String payload = http.getString();

    Serial.println(httpCode);
    Serial.println(payload);
    Serial.println();

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}

// recupera o ip 0.0.0.0 pela API em nuvem (recursivamente até conseguir) e cria os endereços necessários
void getIpAddress() {
  Serial.println("getIpAddress");
  // se houver conexão
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    Serial.println("connected");

    http.begin(wifiClient, "http://SalMolhado.pythonanywhere.com/ip");
    int httpCode = http.GET();
    Serial.println(httpCode);

    if (httpCode > 0) {
      String payload = http.getString();
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, payload);
      payload = doc["value"].as<String>();
      Serial.println(payload);

      http.end();
      
      if (payload != "") {
        // endereços
        char server_address[50];
        strcpy(server_address, "http://");
        strcat(server_address, payload.c_str());
        strcat(server_address, ":8000/");

        strcpy(post_data_endpoint, server_address);
        strcat(post_data_endpoint, "logging/data");

        strcat(server_address, "control/");

        strcpy(get_condition_endpoint, server_address);
        strcat(get_condition_endpoint, "condition");

        strcpy(post_condition_endpoint, get_condition_endpoint);
        strcat(post_condition_endpoint, "/"); 

        strcpy(get_angle_endpoint, server_address);
        strcat(get_angle_endpoint, "angle");

        strcpy(post_angle_endpoint, get_angle_endpoint);
        strcat(post_angle_endpoint, "/");

        Serial.println(post_angle_endpoint);
        Serial.println(get_angle_endpoint);
        Serial.println(post_condition_endpoint);
        Serial.println(get_condition_endpoint);
        Serial.println(post_data_endpoint);
        Serial.println();
      } else {
        delay(10000);
        getIpAddress();
      }
    } else {
      Serial.println("Error on HTTP request");
    }
  } else {
    Serial.println("Error in WiFi connection");
  }
}