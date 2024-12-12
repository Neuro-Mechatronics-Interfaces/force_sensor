# Force Sensor Visualization and Streaming

This repository provides a Python package for connecting to a microcontroller-based force sensor system and visualizing real-time data streams. The package is designed to accommodate an arbitrary number of load cells, with a default of two.

## Features

- **Microcontroller Communication**: Connects to a microcontroller over a serial port to receive real-time force sensor data.
- **Real-Time Visualization**: Uses `pyqtgraph` to plot the data streams dynamically.
- **Scalable Design**: Supports an arbitrary number of load cells (default is two).
- **Debounced Button Handling**: Configurable option for handling button inputs for calibration and offset adjustments.

## Repository Structure

- `force_sensor/`: Python package containing the core functionality.
  - `connection.py`: Manages the serial connection to the microcontroller and data parsing.
  - `plotting.py`: Handles real-time plotting of the data streams.
- `main.py`: Top-level script to run the application, integrating the connection and plotting modules.
- `requirements.txt`: Lists the dependencies required for the project.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Microcontroller firmware sending data in the expected binary format.
- Compatible microcontroller and load cell setup.

### Installation

1. Clone the repository:
```bat
git clone <repository-url> cd force_sensor
```
2. Install the required dependencies:
```bat
pip install -r requirements.txt
```
3. Ensure your microcontroller is connected to a serial port and sending data in the expected manner. To do that, flash the following code (and use appropriate pin connections based on pin names or your appropriate modified counterparts):
```
#include "HX711.h"
#include <Bounce2.h> // Include Bounce2 library
#define USE_BUTTON // Comment this to exclude the button

// Create HX711 objects for each module
HX711 scale1;
HX711 scale2;

// Pin configurations
const int HX711_DT1 = 3;
const int HX711_SCK1 = 2;
const int HX711_DT2 = 5;
const int HX711_SCK2 = 4;

// Calibration parameters (update these after calibration)
float calibrationFactor1 = -5838.f; // Replace with your scale factor for module 1
float calibrationFactor2 = -68086.f; // Replace with your scale factor for module 2
long offset1 = 0;
long offset2 = 0;
float weight1 = 0.f;
float weight2 = 0.f;

struct WeightData {
    uint8_t w1; // Packed weight1
    uint8_t w2; // Packed weight2
};

// Button setup
#ifdef USE_BUTTON
  const int BTN = 6;
  Bounce button = Bounce(); // Create a Bounce object
  // Variables for button press recognition
  unsigned long lastPressTime = 0;
  bool singlePressDetected = false;
  const unsigned long doublePressInterval = 500; // Time in ms to detect double-press
#endif


void setup() {
    #ifdef USE_BUTTON
      pinMode(BTN, INPUT_PULLUP);
      button.attach(BTN);           // Attach the button to Bounce
      button.interval(10);          // Debounce interval (in milliseconds)
    #endif
    Serial.begin(115200);
    // Initialize HX711 modules
    scale1.begin(HX711_DT1, HX711_SCK1);
    scale2.begin(HX711_DT2, HX711_SCK2);

    // Optionally set gain (default is 128)
    scale1.set_gain(64);
    scale1.set_scale(1.f);
    
    scale2.set_gain(64);
    scale2.set_scale(1.f);

    if (scale1.is_ready()) {
      scale1.tare(10);
      offset1 = scale1.read_average(20);
    }
    if (scale2.is_ready()) {
      scale2.tare(10);
      offset2 = scale2.read_average(10);
    }
    Serial.println("Weight1, Weight2");
}

void loop() {
    #ifdef USE_BUTTON
      // Update the button state
      button.update();
      if (button.fell()) {
          unsigned long currentTime = millis();

          if (currentTime - lastPressTime <= doublePressInterval) {
              // Double-press detected
              calibrationFactor1 = (float)(scale1.read_average(20) - offset1);
              calibrationFactor2 = (float)(scale2.read_average(20) - offset2);
              // Serial.println("Double-press detected: Updated calibration factors.");
              // Serial.print("CalibrationFactor1: ");
              // Serial.println(calibrationFactor1);
              // Serial.print("CalibrationFactor2: ");
              // Serial.println(calibrationFactor2);
              // delay(500);
          } else {
              // Single-press detected
              singlePressDetected = true;
          }

          lastPressTime = currentTime;
      }

      // Handle single press
      if (singlePressDetected && millis() - lastPressTime > doublePressInterval) {
          // Reset singlePressDetected to avoid repeated actions
          singlePressDetected = false;

          // Update offsets
          offset1 = scale1.read_average(20);
          offset2 = scale2.read_average(20);
          // Serial.println("Single-press detected: Updated offsets.");
          // Serial.print("Offset1: ");
          // Serial.println(offset1);
          // Serial.print("Offset2: ");
          // Serial.println(offset2);
          // delay(500);
      }
    #endif
    // Check if both scales are ready
    if (scale1.is_ready() && scale2.is_ready()) {
        // Read raw values
        long raw1 = scale1.read();
        delayMicroseconds(5);
        long raw2 = scale2.read();

        // Convert raw values to weights
        weight1 = 0.25 *min(max((raw1 - offset1) / calibrationFactor1, 0.f),1.f) + 0.75 * weight1;
        weight2 = 0.25 *min(max((raw2 - offset2) / calibrationFactor2, 0.f),1.f) + 0.75 * weight2;
        uint8_t w1 = round(255 * weight1);
        uint8_t w2 = round(255 * weight2);

        // Pack weights into struct
        WeightData data;
        data.w1 = round(255 * weight1);
        data.w2 = round(255 * weight2);

        // Send struct as binary data
        Serial.write((uint8_t*)&data, sizeof(data));
    }

    // Delay for update rate
    delay(10);
}
```

Once everything is setup correctly, the application will:
1. Connect to the microcontroller on the specified serial port.
2. Visualize the data streams from the force sensors in real-time.

## Configuration

- Update the `port` variable in `main.py` to match your microcontroller's serial port.
- Adjust `num_channels` in `main.py` to match the number of force sensors in your system.

## Extending the Package

1. **Adding More Channels**:
   - Update the `num_channels` argument in `ForceSensorConnection` and `ForceSensorPlotter` to reflect the desired number of channels.
   - Ensure the microcontroller firmware sends data for the additional channels.

2. **Customizing the Plot**:
   - Modify the `ForceSensorPlotter` class in `plotting.py` to adjust plot styles, colors, or layout.

## Dependencies

- `pyqtgraph`: For real-time plotting.
- `pyserial`: For serial communication.
- `PyQt5`: GUI framework for visualization.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

