#pragma once

class MotorDriver {
public:
    MotorDriver(int pinP1, int pinP2, int pinQ1, int pinQ2);

    void begin();

    // Old function: both wheels drive together.
    void drive(float pwmA, float pwmB);

    // New function: left and right wheels can be controlled separately.
    // Positive = forward, negative = backward, 0 = stop.
    void driveWheels(float leftPwm, float rightPwm);

    void stop();

private:
    int motorPinP1;
    int motorPinP2;
    int motorPinQ1;
    int motorPinQ2;

    static constexpr int maximumLevel = 1000;

    void setupMotorPWM(int pin);
    void writeOneMotor(int forwardPin, int backwardPin, float signedPwm);
    float constrainValue(float value, float minVal, float maxVal);
};