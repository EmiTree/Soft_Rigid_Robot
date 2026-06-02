#ifndef SERVO_ACTUATION_H
#define SERVO_ACTUATION_H

#include "pico/stdlib.h"

#include <stdint.h>

class ServoActuation {
public:
    static const int ServoCount = 4;

    struct ServoMove {
        int servoNumber;
        float speedPercent;
        uint32_t durationMs;
    };

    ServoActuation(int servo1Pin, int servo2Pin, int servo3Pin, int servo4Pin);

    void begin();

    bool setSpeed(int servoNumber, float speedPercent);
    bool runFor(int servoNumber, float speedPercent, uint32_t durationMs);

    bool runMoves(const ServoMove moves[], int moveCount);

    bool runFour(
        float servo1Speed, uint32_t servo1DurationMs,
        float servo2Speed, uint32_t servo2DurationMs,
        float servo3Speed, uint32_t servo3DurationMs,
        float servo4Speed, uint32_t servo4DurationMs
    );

    bool runExamplePattern();

    // add different movements
    bool movement1();

    void stop(int servoNumber);
    void stopAll();
    void update();

    float getSpeed(int servoNumber) const;
    bool isRunning(int servoNumber) const;
    bool isTimedMoveActive(int servoNumber) const;
    bool anyTimedMoveActive() const;

private:
    int servoPins[ServoCount];

    float currentSpeeds[ServoCount];

    bool timedMoveActive[ServoCount];
    absolute_time_t timedMoveEndTimes[ServoCount];

    void setupServoPwm(int pin);
    void writeServoPulse(int servoIndex, float speedPercent);
    void startTimedMoveByIndex(int servoIndex, float speedPercent, uint32_t durationMs);

    int speedToPulseUs(float speedPercent) const;
    float clampSpeed(float speedPercent) const;

    bool servoNumberToIndex(int servoNumber, int &servoIndex) const;
};

#endif