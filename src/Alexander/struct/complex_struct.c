#include "complex_struct.h"
int process_device(DeviceState* device) {
if (!device) {
        return -1;
    }
    if (device->reading_count > 5) {
        return -2;
    }
    double total = 0.0;
    int valid_count = 0;
    for (uint8_t i = 0; i < device->reading_count; i++) {
        if (device->readings[i].status_flags & 0x80) {
            continue;
        }
        double temp = device->readings[i].temperature;
        if (temp < -100.0 || temp > 100.0) {
            continue;
        }
        total += temp;
        valid_count++;
    }
    if (valid_count > 0) {
        if (device->calibration_func) {
            device->calibration_func(valid_count);
        }
    }
    return 0;
}