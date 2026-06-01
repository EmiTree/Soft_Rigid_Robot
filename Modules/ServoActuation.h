#ifndef SERVO_ACTUATION_H
#define SERVO_ACTUATION_H

#include "pico/stdlib.h"

#include <stdint.h>

/*
    ServoActuation controls 4 continuous-rotation servos.

    A continuous-rotation servo does not move to an angle.
    Instead, it rotates at a speed:
        -100 = full speed one direction
           0 = stop
        +100 = full speed the other direction

    Timed moves are non-blocking:
        runFor(...) starts the movement
        update() must be called often in the main loop to stop it on time
*/
class ServoActuation {
public:
    static const int ServoCount = 4;

    ServoActuation(int servo1Pin, int servo2Pin, int servo3Pin, int servo4Pin);

    // Sets up PWM on all 4 servo pins and stops all servos.
    void begin();

    // Sets one servo speed until another command changes it.
    bool setSpeed(int servoNumber, float speedPercent);

    // Runs one servo at a speed for a fixed amount of time.
    bool runFor(int servoNumber, float speedPercent, uint32_t durationMs);

    // Stops one servo.
    void stop(int servoNumber);

    // Stops all 4 servos.
    void stopAll();

    // Checks timed movements and stops servos when their time is finished.
    void update();

    // Returns the current saved speed for one servo.
    float getSpeed(int servoNumber) const;

    // Returns true if the servo currently has a non-zero speed.
    bool isRunning(int servoNumber) const;

private:
    int servoPins[ServoCount];

    // Current speed command for each servo.
    float currentSpeeds[ServoCount];

    // Timed movement state for each servo.
    bool timedMoveActive[ServoCount];
    absolute_time_t timedMoveEndTimes[ServoCount];

    void setupServoPwm(int pin);
    void writeServoPulse(int servoIndex, float speedPercent);

    int speedToPulseUs(float speedPercent) const;
    float clampSpeed(float speedPercent) const;

    // Converts servo number 1-4 into array index 0-3.
    bool servoNumberToIndex(int servoNumber, int &servoIndex) const;
};

#endif