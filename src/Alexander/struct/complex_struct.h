#include <stdint.h>

typedef struct {
    uint32_t sensor_id;
    double temperature;
    uint8_t status_flags;
} SensorReading;

typedef struct {
    char device_name[32];
    SensorReading readings[5];
    uint8_t reading_count;
    void (*calibration_func)(int);
} DeviceState;
int process_device(DeviceState* device);