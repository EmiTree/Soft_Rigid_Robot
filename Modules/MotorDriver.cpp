#include "MotorDriver.h"

#include "pico/stdlib.h"
#include "hardware/pwm.h"

#include <stdint.h>

MotorDriver::MotorDriver(int pinP1, int pinP2, int pinQ1, int pinQ2) {
    motorPinP1 = pinP1;
    motorPinP2 = pinP2;
    motorPinQ1 = pinQ1;
    motorPinQ2 = pinQ2;
}

void MotorDriver::begin() {
    setupMotorPWM(motorPinP1);
    setupMotorPWM(motorPinP2);
    setupMotorPWM(motorPinQ1);
    setupMotorPWM(motorPinQ2);

    stop();
}

void MotorDriver::drive(float pwmA, float pwmB) {
    if (pwmA > 0.0f) {
        driveWheels(pwmA, pwmA);
    } else if (pwmB > 0.0f) {
        driveWheels(-pwmB, -pwmB);
    } else {
        stop();
    }
}

void MotorDriver::driveWheels(float leftPwm, float rightPwm) {
    writeOneMotor(motorPinP1, motorPinP2, leftPwm);
    writeOneMotor(motorPinQ1, motorPinQ2, rightPwm);
}

void MotorDriver::writeOneMotor(int forwardPin, int backwardPin, float signedPwm) {
    signedPwm = constrainValue(signedPwm, -100.0f, 100.0f);

    float pwmPercent = signedPwm;
    if (pwmPercent < 0.0f) {
        pwmPercent = -pwmPercent;
    }

    uint16_t pwmValue = (uint16_t)((pwmPercent / 100.0f) * maximumLevel);
    pwmValue = (uint16_t)constrainValue(pwmValue, 0, maximumLevel);

    if (signedPwm > 0.0f) {
        pwm_set_gpio_level(forwardPin, pwmValue);
        pwm_set_gpio_level(backwardPin, 0);
    } else if (signedPwm < 0.0f) {
        pwm_set_gpio_level(forwardPin, 0);
        pwm_set_gpio_level(backwardPin, pwmValue);
    } else {
        pwm_set_gpio_level(forwardPin, 0);
        pwm_set_gpio_level(backwardPin, 0);
    }
}

void MotorDriver::stop() {
    pwm_set_gpio_level(motorPinP1, 0);
    pwm_set_gpio_level(motorPinQ1, 0);
    pwm_set_gpio_level(motorPinP2, 0);
    pwm_set_gpio_level(motorPinQ2, 0);
}

void MotorDriver::setupMotorPWM(int pin) {
    gpio_set_function(pin, GPIO_FUNC_PWM);

    uint sliceNum = pwm_gpio_to_slice_num(pin);
    pwm_config config = pwm_get_default_config();

    pwm_config_set_clkdiv(&config, 125.0f);
    pwm_config_set_wrap(&config, maximumLevel);

    pwm_init(sliceNum, &config, true);
    pwm_set_gpio_level(pin, 0);
}

float MotorDriver::constrainValue(float value, float minVal, float maxVal) {
    if (value < minVal) return minVal;
    if (value > maxVal) return maxVal;
    return value;
}