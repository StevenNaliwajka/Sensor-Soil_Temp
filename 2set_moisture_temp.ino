// Aurduino Soil/Temp Collection. Scale to QTY of sensors.
// Output format expected: "Set#:SMoist#:SMoistPerc#:STemp#"
// Set # Determines group
// Code will create a folder for every day's worth of data.
// A unique CSV for each Set #

#include <OneWire.h>
#include <DallasTemperature.h>

// Soil moisture sensor pins
const int moisturePin1 = A0;
const int moisturePin2 = A1;

// DS18B20 data wire is connected to digital pins
#define ONE_WIRE_BUS1 2
#define ONE_WIRE_BUS2 3

// Setup a OneWire instance
OneWire oneWire1(ONE_WIRE_BUS1);
OneWire oneWire2(ONE_WIRE_BUS2);

// Pass OneWire reference to Dallas Temperature library
DallasTemperature sensors1(&oneWire1);
DallasTemperature sensors2(&oneWire2);

// Calibration values for soil moisture sensor
const int dryValue = 1023; // Adjust based on calibration
const int wetValue = 242;  // Adjust based on calibration

void setup() {
  Serial.begin(9600);
  sensors1.begin();
  sensors2.begin();
}

void loop() {
  // Read soil moisture values
  int moistureValue1 = analogRead(moisturePin1);
  int moistureValue2 = analogRead(moisturePin2);

  // Convert moisture values to percentage
  int moisturePercent1 = map(moistureValue1, dryValue, wetValue, 0, 100);
  moisturePercent1 = constrain(moisturePercent1, 0, 100);

  int moisturePercent2 = map(moistureValue2, dryValue, wetValue, 0, 100);
  moisturePercent2 = constrain(moisturePercent2, 0, 100);

  // Request temperature readings
  sensors1.requestTemperatures();
  sensors2.requestTemperatures();

  float temperatureC1 = sensors1.getTempCByIndex(0);
  float temperatureC2 = sensors2.getTempCByIndex(0);

  // Validate temperature readings (Dallas sensors return -127°C if not connected)
  if (temperatureC1 == -127.00) {
    Serial.println("Error: Sensor 1 not detected.");
  }
  if (temperatureC2 == -127.00) {
    Serial.println("Error: Sensor 2 not detected.");
  }

  // Print Set1 readings
  Serial.print("Set1:SMoist");
  Serial.print(moistureValue1);
  Serial.print(":SMoistPerc");
  Serial.print(moisturePercent1);
  Serial.print(":STemp");
  Serial.println(temperatureC1);


  // Print Set2 readings
  Serial.print("Set2:SMoist");
  Serial.print(moistureValue2);
  Serial.print(":SMoistPerc");
  Serial.print(moisturePercent2);
  Serial.print(":STemp");
  if (temperatureC2 != -127.00) {
    Serial.println(temperatureC2);
  } else {
    Serial.println("N/A");
  }


  Serial.flush(); // Ensure all data is written before delay
  delay(1000); // Wait 1 second before the next reading
}
